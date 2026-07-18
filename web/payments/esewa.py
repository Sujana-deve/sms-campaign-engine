import base64
import hashlib
import hmac
import json
import uuid
from decimal import Decimal

from django.conf import settings
from django.db import transaction as db_transaction

from .models import Balance, Transaction


class EsewaVerificationError(Exception):
    """Raised when a callback's signature or status check fails verification."""
    pass


def generate_transaction_uuid() -> str:
    """Unique ID per payment attempt. eSewa requires this to be unique per request."""
    return str(uuid.uuid4())


def _signature_fields(total_amount, transaction_uuid, product_code):
    """
    eSewa v2 signs exactly these three fields, in exactly this order,
    as a comma-separated string. Order matters — it's part of the spec,
    not a formatting choice.
    """
    return f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"


def generate_signature(total_amount, transaction_uuid, product_code) -> str:
    """HMAC-SHA256 over the signed fields, base64-encoded. Uses the secret key from settings."""
    message = _signature_fields(total_amount, transaction_uuid, product_code)
    secret = settings.ESEWA_SECRET_KEY.encode('utf-8')
    digest = hmac.new(secret, message.encode('utf-8'), hashlib.sha256).digest()
    return base64.b64encode(digest).decode('utf-8')


def build_payment_form_data(amount, purpose: str = "") -> dict:
    """
    Builds the full field set eSewa's form-POST expects.
    `purpose` is a free-text label for your own records — NOT sent to eSewa,
    stripped before building the payload. Not stored anywhere: this app's
    only job right now is topping up the single global Balance, so there's
    nothing to disambiguate yet.
    """
    transaction_uuid = generate_transaction_uuid()
    total_amount = str(amount)
    product_code = settings.ESEWA_PRODUCT_CODE

    signature = generate_signature(total_amount, transaction_uuid, product_code)

    return {
        "amount": total_amount,
        "tax_amount": "0",
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
        "product_code": product_code,
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "success_url": settings.ESEWA_SUCCESS_URL,
        "failure_url": settings.ESEWA_FAILURE_URL,
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "signature": signature,
    }


def decode_callback_payload(encoded_data: str) -> dict:
    """
    eSewa's success redirect appends a base64-encoded JSON blob as ?data=...
    Decoding this tells you what eSewa *claims* happened — it is NOT proof
    of payment. These params are client-controlled (they pass through the
    user's browser) and can be replayed or spoofed manually. Never credit
    anything based on this alone — see verify_transaction_status below.
    """
    try:
        decoded = base64.b64decode(encoded_data).decode('utf-8')
        return json.loads(decoded)
    except (ValueError, json.JSONDecodeError) as e:
        raise EsewaVerificationError(f"Malformed callback payload: {e}")


def verify_transaction_status(transaction_uuid: str, total_amount: str) -> dict:
    """
    The mandatory server-side check. Calls eSewa's status API directly —
    server to server, not through the user's browser — and trusts THIS
    response, not the redirect params. This is the one call that actually
    proves money moved.

    Raises EsewaVerificationError if eSewa doesn't confirm COMPLETE status.
    Returns the raw verified response dict on success.
    """
    import requests

    params = {
        "product_code": settings.ESEWA_PRODUCT_CODE,
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
    }

    try:
        response = requests.get(
            settings.ESEWA_STATUS_CHECK_URL,
            params=params,
            timeout=10,
        )
        response.raise_for_status()
    except requests.RequestException as e:
        raise EsewaVerificationError(f"Status check request failed: {e}")

    try:
        result = response.json()
    except ValueError:
        raise EsewaVerificationError(f"Status check returned non-JSON: {response.text[:200]}")

    status = result.get("status")
    if status != "COMPLETE":
        raise EsewaVerificationError(f"Transaction not complete. eSewa status: {status!r}")

    return result


def handle_verified_payment(verified_result: dict, transaction_uuid: str, amount: str):
    """
    Credits the global Balance now that eSewa's status API has independently
    confirmed COMPLETE — verified_result is that confirmed response, passed
    through for any future auditing/logging need, not used further here
    since verify_transaction_status() already scoped its check to this
    exact transaction_uuid + amount pair.

    Idempotent by design: eSewa's success redirect can legitimately fire
    more than once for the same payment (browser refresh/back-button on
    the success page re-sends the same ?data=... callback). Without a
    guard, a refresh would silently double-credit the balance. The guard
    here is inside the same atomic block as the row lock, so two
    near-simultaneous calls for the same transaction_uuid can't both pass
    the check before either commits — the second one blocks on the lock,
    then correctly sees the Transaction already recorded.
    """
    with db_transaction.atomic():
        balance = Balance.get_locked_singleton()

        already_credited = Transaction.objects.filter(
            reference=transaction_uuid,
            type=Transaction.Type.TOPUP,
        ).exists()

        if already_credited:
            return

        balance.top_up(Decimal(str(amount)), reference=transaction_uuid)