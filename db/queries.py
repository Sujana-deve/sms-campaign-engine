from db.connection import get_connection

def get_all_contacts():
    conn = get_connection()
    if conn is None:
        return []
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, business_name, owner_name, 
               phone, city, category, attributes
        FROM contacts
        WHERE is_active = TRUE
    """)
    
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    contacts = []
    for row in rows:
        contacts.append({
            "id":            row[0],
            "business_name": row[1],
            "owner_name":    row[2],
            "phone":         row[3],
            "city":          row[4],
            "category":      row[5],
            "attributes":    row[6],
        })
    return contacts


def get_opted_out_phones():
    conn = get_connection()
    if conn is None:
        return []
    
    cursor = conn.cursor()
    cursor.execute("SELECT phone FROM opt_outs")
    
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return [row[0] for row in rows]


def save_message(campaign_id, contact_id, phone, body, status, gateway):
    conn = get_connection()
    if conn is None:
        print("  [ERROR] No DB connection - message not saved")
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO messages 
                (campaign_id, contact_id, phone, body, status, gateway, sent_at)
            VALUES 
                (%s, %s, %s, %s, %s, %s, NOW())
            RETURNING id
        """, (campaign_id, contact_id, phone, body, status, gateway))

        message_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return message_id

    except Exception as e:
        print(f"  [ERROR] Failed to save message: {e}")
        conn.rollback()
        conn.close()
        return None