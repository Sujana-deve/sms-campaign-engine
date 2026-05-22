"""the main functionality of this module is to check if any
 contact's phone number is in the list of opted-out phone numbers.
 It returns two lists: one with clean contacts and another with contacts that have opted out,
   along with the reason for skipping them.
"""
from db.queries import get_opted_out_phones

def check_opt_outs(contacts):
    clean = []
    opted_out = []

    opted_out_phones = set(get_opted_out_phones())

    for contact in contacts:
        phone = str(contact.get('phone', '')).strip()

        if phone in opted_out_phones:
            contact['skip_reason'] = 'Opted out'
            opted_out.append(contact)
        else:
            clean.append(contact)

    return clean, opted_out