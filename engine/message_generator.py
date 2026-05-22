SMS_MAX_LENGTH = 160  # Standard SMS limit for plain text


def generate_messages(contacts, template):
    results = []

    for contact in contacts:
        try:
            message = template.format_map(contact)
        except KeyError as e:
            contact['skip_reason'] = f"Missing template key: {e}"
            continue

        # Message length check
        msg_length = len(message)
        if msg_length > SMS_MAX_LENGTH:
            print(f"  [WARNING] Message for {contact.get('phone')} is {msg_length} chars "
                  f"(limit {SMS_MAX_LENGTH}). Will be split into multiple SMS — extra cost.")
            contact['length_warning'] = True
        else:
            contact['length_warning'] = False

        results.append({
            'contact': contact,
            'message': message,
            'length': msg_length
        })

    return results