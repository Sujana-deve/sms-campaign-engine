from db.connection import get_connection
from datetime import datetime
import os

def get_campaign_summary(campaign_id):
    conn = get_connection()
    if conn is None:
        return None

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT cl.total_contacts, cl.sent, cl.delivered, 
                   cl.failed, cl.opted_out_skipped, cl.cost_npr, 
                   cl.completed_at, c.name, c.template
            FROM campaign_logs cl
            JOIN campaigns c ON c.id = cl.campaign_id
            WHERE cl.campaign_id = %s
            ORDER BY cl.completed_at DESC
            LIMIT 1
        """, (campaign_id,))

        row = cursor.fetchone()
        cursor.close()
        conn.close()

        if row is None:
            return None

        return {
            'total_contacts':   row[0],
            'sent':             row[1],
            'delivered':        row[2],
            'failed':           row[3],
            'opted_out_skipped': row[4],
            'cost_npr':         row[5],
            'completed_at':     row[6],
            'campaign_name':    row[7],
            'template':         row[8],
        }

    except Exception as e:
        print(f"  [ERROR] Failed to fetch campaign summary: {e}")
        conn.close()
        return None


def get_campaign_messages(campaign_id):
    conn = get_connection()
    if conn is None:
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT c.business_name, m.phone, m.body, 
                   m.status, m.sent_at
            FROM messages m
            LEFT JOIN contacts c ON c.id = m.contact_id
            WHERE m.campaign_id = %s
            ORDER BY m.sent_at ASC
        """, (campaign_id,))

        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        messages = []
        for row in rows:
            messages.append({
                'business_name': row[0] or 'Unknown',
                'phone':         row[1],
                'body':          row[2],
                'status':        row[3],
                'sent_at':       row[4],
            })
        return messages

    except Exception as e:
        print(f"  [ERROR] Failed to fetch messages: {e}")
        conn.close()
        return []


def generate_report(campaign_id):
    summary = get_campaign_summary(campaign_id)
    messages = get_campaign_messages(campaign_id)

    if summary is None:
        print("  [ERROR] No campaign data found")
        return None

    delivered_rate = 0
    if summary['sent'] > 0:
        delivered_rate = round((summary['delivered'] / summary['sent']) * 100, 1)

    rows_html = ""
    for m in messages:
        status_color = "#28a745" if m['status'] == 'delivered' else "#dc3545"
        sent_at = m['sent_at'].strftime("%Y-%m-%d %H:%M:%S") if m['sent_at'] else "N/A"
        rows_html += f"""
        <tr>
            <td>{m['business_name']}</td>
            <td>{m['phone']}</td>
            <td>{m['body']}</td>
            <td style="color:{status_color}; font-weight:bold;">{m['status'].upper()}</td>
            <td>{sent_at}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Campaign Report - {summary['campaign_name']}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }}
        h1 {{ color: #333; }}
        .summary {{ display: flex; gap: 20px; margin-bottom: 30px; }}
        .card {{ background: white; padding: 20px; border-radius: 8px; 
                 min-width: 140px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        .card h2 {{ margin: 0; font-size: 36px; color: #333; }}
        .card p {{ margin: 5px 0 0; color: #888; font-size: 14px; }}
        table {{ width: 100%; border-collapse: collapse; background: white; 
                 border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        th {{ background: #333; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 10px 12px; border-bottom: 1px solid #eee; }}
        tr:last-child td {{ border-bottom: none; }}
    </style>
</head>
<body>
    <h1>Campaign Report: {summary['campaign_name']}</h1>
    <p>Completed at: {summary['completed_at']} | Template: <em>{summary['template']}</em></p>

    <div class="summary">
        <div class="card"><h2>{summary['total_contacts']}</h2><p>Total Contacts</p></div>
        <div class="card"><h2>{summary['sent']}</h2><p>Sent</p></div>
        <div class="card"><h2>{summary['delivered']}</h2><p>Delivered</p></div>
        <div class="card"><h2>{summary['failed']}</h2><p>Failed</p></div>
        <div class="card"><h2>{delivered_rate}%</h2><p>Delivery Rate</p></div>
        <div class="card"><h2>Rs.{summary['cost_npr']}</h2><p>Total Cost</p></div>
        <div class="card"><h2>{summary['opted_out_skipped']}</h2><p>Opted Out</p></div>
    </div>

    <table>
        <thead>
            <tr>
                <th>Business Name</th>
                <th>Phone</th>
                <th>Message</th>
                <th>Status</th>
                <th>Sent At</th>
            </tr>
        </thead>
        <tbody>
            {rows_html}
        </tbody>
    </table>
</body>
</html>"""

    os.makedirs("reports", exist_ok=True)
    filename = f"reports/campaign_{campaign_id[:8]}.html"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"  [REPORT] Generated: {filename}")
    return filename