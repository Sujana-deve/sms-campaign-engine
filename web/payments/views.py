from django.shortcuts import render
from django.http import HttpResponseBadRequest
from django.conf import settings

from .esewa import (
    build_payment_form_data,
    decode_callback_payload,
    verify_transaction_status,
    handle_verified_payment,
    EsewaVerificationError,
)


def initiate_payment(request):
    """
    GET ?amount=500 for now — no auth, no purpose tracking, no model.
    This is a bare-bones test harness so you can confirm the sandbox flow
    works end-to-end before anything real depends on it.
    """
    amount = request.GET.get('amount')
    if not amount:
        return HttpResponseBadRequest("Missing 'amount' query param — e.g. /payments/initiate/?amount=100")

    try:
        float(amount)
    except ValueError:
        return HttpResponseBadRequest(f"'{amount}' is not a valid amount")

    form_data = build_payment_form_data(amount)

    return render(request, 'payments/redirect_to_esewa.html', {
        'form_data': form_data,
        'esewa_form_url': settings.ESEWA_FORM_URL,
    })


def payment_success(request):
    """
    eSewa redirects the browser here with ?data=<base64 blob> after the user
    completes payment. We decode it for the transaction_uuid, then throw that
    decoded data away and verify independently against eSewa's status API.
    Only the independent check result is trusted.
    """
    encoded_data = request.GET.get('data')
    if not encoded_data:
        return HttpResponseBadRequest("Missing 'data' param on callback")

    try:
        callback_payload = decode_callback_payload(encoded_data)
        transaction_uuid = callback_payload.get('transaction_uuid')
        total_amount = callback_payload.get('total_amount')

        if not transaction_uuid or not total_amount:
            raise EsewaVerificationError("Callback payload missing transaction_uuid or total_amount")

        verified = verify_transaction_status(transaction_uuid, total_amount)
        handle_verified_payment(verified, transaction_uuid, total_amount)

        return render(request, 'payments/success.html', {
            'transaction_uuid': transaction_uuid,
            'amount': total_amount,
        })

    except EsewaVerificationError as e:
        return render(request, 'payments/verification_failed.html', {'error': str(e)}, status=402)


def payment_failure(request):
    """eSewa redirects here if the user cancels or payment fails on their end."""
    return render(request, 'payments/failure.html')