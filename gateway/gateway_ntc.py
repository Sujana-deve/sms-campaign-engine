import requests
from datetime import datetime, timezone
from config.settings import NTC_TOKEN, NTC_SENDER_ID
from db.queries import save_message

# TODO: Replace with actual endpoint URL from NTC after contract and credential handover
# NTC provides this privately after SMS Alert contract signing (vas@ntc.net.np)
NTC_API_URL = "https://smsalert.ntc.net.np/api/send/"  # PLACEHOLDER — confirm with NTC


class NTCGateway:

    def send(self, phone, message, contact_id, campaign_id):
        # TODO: Confirm exact field names with NTC API documentation
        # Common variations NTC may use:
        #   phone field: "mobile", "to", "number", "msisdn"
        #   message field: "msg", "text", "message", "sms"
        #   auth field: "token", "api_key", "auth_token", "password"
        #   sender field: "from", "sender", "sender_id", "source"
        # Update payload fields once NTC hands over their spec
        payload = {
            "token": NTC_TOKEN,          # TODO: confirm field name
            "from": NTC_SENDER_ID,       # TODO: confirm field name
            "to": phone,                 # NTC expects 10-digit local format (98XXXXXXXX) — already stripped by validator
            "text": message,             # TODO: confirm field name
        }

        try:
            response = requests.post(NTC_API_URL, data=payload, timeout=10)
            result = response.json()

            # TODO: Confirm NTC's success response structure
            # Sparrow uses response_code == 200; NTC may use "status", "code", "success", etc.
            # Update this condition once NTC spec is confirmed
            if response.status_code == 200 and result.get("response_code") == 200:
                status = "queued"
            else:
                error_msg = result.get("response", "Unknown error")  # TODO: confirm NTC error field name
                print(f"[NTCGateway] Failed for {phone}: {error_msg}")
                status = "failed"

        except requests.exceptions.Timeout:
            print(f"[NTCGateway] Timeout for {phone}")
            status = "failed"
            result = {"response": "Request timed out"}

        except requests.exceptions.RequestException as e:
            print(f"[NTCGateway] Request error for {phone}: {e}")
            status = "failed"
            result = {"response": str(e)}

        message_id = save_message(
            campaign_id=campaign_id,
            contact_id=contact_id,
            phone=phone,
            body=message,
            status=status,
            gateway="ntc",
        )

        return {
            "status": status,
            "phone": phone,
            "message_id": message_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "gateway_response": result,
        }