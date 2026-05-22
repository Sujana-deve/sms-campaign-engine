from db.queries import get_all_contacts

def fetch_contacts(filters=None):
    contacts = get_all_contacts()

    if filters is None:
        return contacts

    filtered = []
    for contact in contacts:
        match = True
        for key, value in filters.items():
            if contact.get(key) != value:
                match = False
                break
        if match:
            filtered.append(contact)

    return filtered