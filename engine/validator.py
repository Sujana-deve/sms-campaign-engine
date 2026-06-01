import re

# Matches a valid normalized Nepali number: +9779[78]XXXXXXXX
valid_phone_pattern = re.compile(r'^\+977[9][78]\d{8}$')

REQUIRED_FIELDS = ['phone', 'business_name', 'owner_name', 'city']


def normalize_phone(phone):
    """
    Cleans and standardizes any Nepali phone number into +977XXXXXXXXXX format.
    Handles:
        9841234567        -> +9779841234567
        09841234567       -> +9779841234567
        9779841234567     -> +9779841234567
        +977 984 123 4567 -> +9779841234567
        +977-984-123-4567 -> +9779841234567
    Returns None if the number can't be normalized.
    """
    # Remove all spaces, dashes, parentheses
    phone = re.sub(r'[\s\-\(\)]', '', str(phone).strip())

    # Remove leading +
    if phone.startswith('+'):
        phone = phone[1:]

    # Now phone is purely digits
    # Case 1: starts with 977 -> just add +
    if phone.startswith('977'):
        return '+' + phone

    # Case 2: starts with 0 -> remove 0, add +977
    if phone.startswith('0'):
        return '+977' + phone[1:]

    # Case 3: bare 10-digit number starting with 9 -> add +977
    if len(phone) == 10 and phone.startswith('9'):
        return '+977' + phone

    # Can't normalize
    return None


def validate_contacts(contacts):
    valid = []
    invalid = []
    seen_phones = set()

    for contact in contacts:
        raw_phone = str(contact.get('phone', '')).strip()

        # Step 1: Check required fields first
        missing = [f for f in REQUIRED_FIELDS if not contact.get(f)]
        if missing:
            contact['invalid_reason'] = f"Missing fields: {', '.join(missing)}"
            invalid.append(contact)
            continue

        # Step 2: Normalize the phone number
        normalized = normalize_phone(raw_phone)
        if not normalized:
            contact['invalid_reason'] = f"Cannot normalize phone: {raw_phone}"
            invalid.append(contact)
            continue

        # Step 3: Validate normalized format
        if not valid_phone_pattern.match(normalized):
            contact['invalid_reason'] = f"Invalid phone after normalization: {normalized}"
            invalid.append(contact)
            continue

        # Step 4: Deduplicate
        if normalized in seen_phones:
            contact['invalid_reason'] = f"Duplicate phone: {normalized}"
            invalid.append(contact)
            continue

        # Update contact with normalized phone so rest of pipeline uses clean number
        contact['phone'] = normalized
        seen_phones.add(normalized)
        valid.append(contact)

    return valid, invalid