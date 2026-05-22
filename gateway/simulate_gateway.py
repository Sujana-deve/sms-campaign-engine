from gateway.base_gateway import BaseGateway
from db.queries import save_message
from datetime import datetime

class SimulateGateway(BaseGateway):
    def send(self, phone, message, contact_id=None, campaign_id=None):
        print(f"  [SIMULATE] Sending to {phone}: {message}")

        message_id = save_message(
            campaign_id=campaign_id,
            contact_id=contact_id,
            phone=phone,
            body=message,
            status='delivered',
            gateway='simulate'
        )

        return {
            'status': 'delivered',
            'phone': phone,
            'message_id': str(message_id),
            'timestamp': datetime.now().isoformat()
        }