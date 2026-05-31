import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.contact_fetcher import fetch_contacts
from engine.validator import validate_contacts
from engine.opt_out_checker import check_opt_outs
from engine.message_generator import generate_messages
from job_queue.job_queue import JobQueue
from job_queue.rate_limiter import RateLimiter
from tracker.delivery_tracker import track_delivery
from tracker.campaign_logger import log_campaign
from analytics.report import generate_report
from db.connection import get_connection
from config.settings import GATEWAY_MODE

MAX_RETRIES = 3


def update_campaign_status(campaign_id, status):
    conn = get_connection()
    if conn is None:
        print(f"  [ERROR] Could not update campaign status to '{status}' — no DB connection")
        return
    try:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE campaigns SET status = %s WHERE id = %s",
            (status, campaign_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"  [ERROR] Failed to update campaign status: {e}")
        conn.rollback()
        conn.close()


def send_with_retry(gateway, phone, message, contact_id, campaign_id):
    attempt = 0
    result = None

    while attempt < MAX_RETRIES:
        attempt += 1
        print(f"    Attempt {attempt} for {phone}...")

        result = gateway.send(
            phone=phone,
            message=message,
            contact_id=contact_id,
            campaign_id=campaign_id
        )

        if result['status'] in ('delivered', 'queued'):
            if attempt > 1:
                print(f"    Success on attempt {attempt}.")
            return result

        print(
            f"    Failed on attempt {attempt}. Retrying..."
            if attempt < MAX_RETRIES
            else f"    Failed after {MAX_RETRIES} attempts. Giving up."
        )

    return result


def run_campaign(campaign_id, template, filters=None):
    print("\n--- CAMPAIGN RUNNER STARTED ---\n")

    update_campaign_status(campaign_id, 'running')

    try:
        # Step 1: Fetch
        print("Step 1: Fetching contacts...")
        contacts = fetch_contacts(filters)
        print(f"  Fetched: {len(contacts)}")

        # Step 2: Validate
        print("Step 2: Validating contacts...")
        valid, invalid = validate_contacts(contacts)
        print(f"  Valid: {len(valid)} | Invalid: {len(invalid)}")

        # Step 3: Opt-out check
        print("Step 3: Checking opt-outs...")
        clean, opted_out = check_opt_outs(valid)
        print(f"  Clean: {len(clean)} | Opted out: {len(opted_out)}")

        # Step 4: Generate messages
        print("Step 4: Generating messages...")
        sms_messages = generate_messages(clean, template)
        print(f"  Messages generated: {len(sms_messages)}")

        # Step 5: Load queue
        print("Step 5: Loading job queue...")
        job_queue = JobQueue()
        job_queue.load(sms_messages)

        # Step 6: Setup gateway and rate limiter
        if GATEWAY_MODE == 'sparrow':
            from gateway.sparrow_gateway import SparrowGateway
            gateway = SparrowGateway()
            print("Step 6: Gateway — Sparrow (live)")
        else:
            from gateway.simulate_gateway import SimulateGateway
            gateway = SimulateGateway()
            print("Step 6: Gateway — Simulate (no messages will be sent)")

        rate_limiter = RateLimiter()

        # Step 7: Send
        print("Step 7: Sending messages...\n")
        sent = 0
        delivered = 0
        failed = 0

        while not job_queue.is_empty():
            job = job_queue.next_job()
            contact = job['contact']
            message = job['message']

            rate_limiter.wait()

            result = send_with_retry(
                gateway=gateway,
                phone=contact['phone'],
                message=message,
                contact_id=str(contact['id']),
                campaign_id=campaign_id
            )

            message_id = result.get('message_id')
            if message_id:
                track_delivery(message_id, result)

            sent += 1
            if result['status'] in ('delivered', 'queued'):
                delivered += 1
            else:
                failed += 1

        # Step 8: Log campaign
        print("\nStep 8: Logging campaign...")
        log_campaign(
            campaign_id=campaign_id,
            total_contacts=len(contacts),
            sent=sent,
            delivered=delivered,
            failed=failed,
            opted_out_skipped=len(opted_out)
        )

        # Step 9: Generate report
        print("Step 9: Generating report...")
        report_path = generate_report(campaign_id)

        update_campaign_status(campaign_id, 'completed')

        print(f"\n--- CAMPAIGN COMPLETE ---")
        print(f"  Sent: {sent} | Delivered: {delivered} | Failed: {failed}")
        print(f"  Report: {report_path}\n")

    except Exception as e:
        print(f"\n[CRITICAL ERROR] Campaign {campaign_id} failed: {e}")
        update_campaign_status(campaign_id, 'failed')
        raise


if __name__ == "__main__":
    CAMPAIGN_ID = "fc6c64cb-34cd-4ab9-bb3e-160154302584"
    TEMPLATE = "Hello {owner_name}, this is a special offer for {business_name} in {city}!"

    run_campaign(CAMPAIGN_ID, TEMPLATE)