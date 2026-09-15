import os
import pickle
from urllib.request import Request
import google.auth
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying contacts, you will need the appropriate scopes
SCOPES = ['https://www.googleapis.com/auth/contacts']

# Authenticate and build the API client
def authenticate_google_account():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens.
    # It is created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Build the API client
    try:
        service = build('people', 'v1', credentials=creds)
        return service
    except HttpError as err:
        print(f'An error occurred: {err}')

# Get contacts from Google account
def get_contacts(service):
    results = service.people().connections().list(
        resourceName='people/me',
        personFields='names,emailAddresses').execute()
    connections = results.get('connections', [])

    contacts = []
    if not connections:
        print('No contacts found.')
    else:
        for person in connections:
            names = person.get('names', [])
            if names:
                name = names[0].get('displayName')
                contacts.append(name)

    return contacts

# Rename contacts: Split first and last name and join in reverse order
def rename_contacts(contacts):
    renamed_contacts = []
    for contact in contacts:
        name_parts = contact.split()
        if len(name_parts) == 2:  # assuming first name and last name
            renamed_contact = " ".join(reversed(name_parts))
        else:
            renamed_contact = contact  # If no space in the name, leave it unchanged
        renamed_contacts.append(renamed_contact)
    return renamed_contacts

# Update contacts in Google account (NOTE: Google People API doesn't allow changing contact names directly)
def update_contacts(service, renamed_contacts):
    # NOTE: The Google People API currently does not support directly modifying a contact's name.
    # You can create a new contact or modify other fields like phone numbers or emails.
    print("Renamed Contacts:")
    for name in renamed_contacts:
        print(name)

def main():
    # Step 1: Authenticate
    service = authenticate_google_account()

    # Step 2: Get contacts
    contacts = get_contacts(service)

    # Step 3: Rename contacts
    renamed_contacts = rename_contacts(contacts)

    # Step 4: Update contacts (you would have to create or modify contacts, currently we are just printing renamed names)
    update_contacts(service, renamed_contacts)

if __name__ == '__main__':
    main()
