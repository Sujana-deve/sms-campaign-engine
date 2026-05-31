import requests
from datetime import datetime, timezone
from config.settings import SPARROW_TOKEN, SPARROW_SENDER_ID
from db.queries import save_message

SPARROW_API_URL = "http://api.sparrowsms.com/v2/sms/"


class SparrowGateway:

    def send(self, phone, message, contact_id, campaign_id):
        payload = {
            "token": SPARROW_TOKEN,
            "from": SPARROW_SENDER_ID,
            "to": phone.replace('+977', '', 1),  # FIX 1: Sparrow expects 977XXXXXXXXXX not +977XXXXXXXXXX
            "text": message,
        }

        try:
            response = requests.post(SPARROW_API_URL, data=payload, timeout=10)
            result = response.json()

            if response.status_code == 200 and result.get("response_code") == 200:
                status = "queued"  # FIX 2: Sparrow queues on acceptance, not actual delivery
            else:
                # Use Sparrow's own error message for easier debugging
                error_msg = result.get("response", "Unknown error")
                print(f"[SparrowGateway] Failed for {phone}: {error_msg}")
                status = "failed"

        except requests.exceptions.Timeout:
            print(f"[SparrowGateway] Timeout for {phone}")
            status = "failed"
            result = {"response": "Request timed out"}

        except requests.exceptions.RequestException as e:
            print(f"[SparrowGateway] Request error for {phone}: {e}")
            status = "failed"
            result = {"response": str(e)}

        message_id = save_message(
            campaign_id=campaign_id,
            contact_id=contact_id,
            phone=phone,
            body=message,
            status=status,
            gateway="sparrow",
        )

        return {
            "status": status,
            "phone": phone,
            "message_id": message_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "gateway_response": result,
        }