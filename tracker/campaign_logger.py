from db.connection import get_connection
from config.settings import SMS_COST_NPR

def log_campaign(campaign_id, total_contacts, sent, delivered, failed, opted_out_skipped):
    conn = get_connection()
    if conn is None:
        print("  [ERROR] No DB connection - campaign not logged")
        return False

    try:
        cost_npr = delivered * SMS_COST_NPR

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO campaign_logs
                (campaign_id, total_contacts, sent, delivered, failed, opted_out_skipped, cost_npr, completed_at)
            VALUES
                (%s, %s, %s, %s, %s, %s, %s, NOW())
        """, (campaign_id, total_contacts, sent, delivered, failed, opted_out_skipped, cost_npr))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"  [LOGGER] Campaign {campaign_id} logged | Sent: {sent} | Delivered: {delivered} | Failed: {failed} | Cost: Rs.{cost_npr}")
        return True

    except Exception as e:
        print(f"  [ERROR] Failed to log campaign: {e}")
        conn.rollback()
        conn.close()
        return False