from db.connection import get_connection

def track_delivery(message_id, result):
    conn = get_connection()
    if conn is None:
        print("  [ERROR] No DB connection - delivery not tracked")
        return False

    try:
        status = result.get('status', 'failed')
        cursor = conn.cursor()

        if status == 'delivered':
            cursor.execute("""
                UPDATE messages
                SET status = %s,
                    delivered_at = NOW()
                WHERE id = %s
            """, (status, message_id))

        else:
            cursor.execute("""
                UPDATE messages
                SET status = %s,
                    failed_at = NOW()
                WHERE id = %s
            """, (status, message_id))

        conn.commit()
        cursor.close()
        conn.close()
        print(f"  [TRACKER] Message {message_id} marked as {status}")
        return True

    except Exception as e:
        print(f"  [ERROR] Failed to track delivery: {e}")
        conn.rollback()
        conn.close()
        return False