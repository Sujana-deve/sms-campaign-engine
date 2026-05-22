import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from engine.contact_fetcher import fetch_contacts
from engine.validator import validate_contacts
from engine.opt_out_checker import check_opt_outs
from engine.message_generator import generate_messages

template = "Hello {owner_name}, this is a special offer for {business_name} in {city}!"

print("Step 1: Fetching contacts...")
contacts = fetch_contacts()
print(f"  Fetched: {len(contacts)}")

print("Step 2: Validating...")
valid, invalid = validate_contacts(contacts)
print(f"  Valid: {len(valid)}, Invalid: {len(invalid)}")
for c in invalid:
    print(f"    INVALID - {c.get('business_name')} | {c.get('invalid_reason')}")

print("Step 3: Checking opt-outs...")
clean, opted_out = check_opt_outs(valid)
print(f"  Clean: {len(clean)}, Opted out: {len(opted_out)}")
for c in opted_out:
    print(f"    OPTED OUT - {c.get('business_name')}")

print("Step 4: Generating messages...")
messages = generate_messages(clean, template)
print(f"  Messages generated: {len(messages)}")
for m in messages:
    print(f"    → {m['contact']['business_name']}: {m['message']}")