import os
import sys
import base64
from email.message import EmailMessage
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Scope for composing and editing drafts
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

def create_draft(to_email, subject, body, pdf_path):
    creds = None
    # Token.json stores your access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        # Build the Gmail API service
        service = build('gmail', 'v1', credentials=creds)

        # Construct the email
        message = EmailMessage()
        message.set_content(body)
        message['To'] = to_email
        message['From'] = 'prakharsinghal10a@gmail.com'
        message['Subject'] = subject

        # Read and attach the PDF
        with open(pdf_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
            message.add_attachment(
                pdf_data, 
                maintype='application', 
                subtype='pdf', 
                filename=os.path.basename(pdf_path)
            )

        # Encode the message properly for the Gmail API
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        create_draft_request_body = {'message': {'raw': encoded_message}}
        
        # Execute the API call
        draft = service.users().drafts().create(
            userId="me", 
            body=create_draft_request_body
        ).execute()
        
        print(f"Success! Draft created with ID: {draft['id']}")
        
    except HttpError as error:
        print(f"An API error occurred: {error}")
    except FileNotFoundError:
        print(f"Error: Could not find the file '{pdf_path}' or 'credentials.json'.")

if __name__ == '__main__':
    # Ensure correct number of arguments are passed from Antigravity
    if len(sys.argv) < 5:
        print("Usage: python create_draft.py <to_email> <subject> <body> <pdf_path>")
        sys.exit(1)
        
    create_draft(
        to_email=sys.argv[1], 
        subject=sys.argv[2], 
        body=sys.argv[3], 
        pdf_path=sys.argv[4]
    )