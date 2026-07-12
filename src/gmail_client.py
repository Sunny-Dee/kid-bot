import os
import base64
from typing import List, Dict
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

def get_gmail_service():
    """Authenticates and returns the Gmail API service using env vars."""
    client_id = os.environ.get("GMAIL_CLIENT_ID")
    client_secret = os.environ.get("GMAIL_CLIENT_SECRET")
    refresh_token = os.environ.get("GMAIL_REFRESH_TOKEN")
    
    creds = Credentials(
        token=None,
        refresh_token=refresh_token,
        client_id=client_id,
        client_secret=client_secret,
        token_uri="https://oauth2.googleapis.com/token"
    )
    return build('gmail', 'v1', credentials=creds)

def extract_email_body(payload: dict) -> str:
    """Recursively extracts plain text from the email payload."""
    body = ""
    if 'data' in payload.get('body', {}):
        body += base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')
    
    if 'parts' in payload:
        for part in payload['parts']:
            if part.get('mimeType') == 'text/plain':
                body += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
            elif 'parts' in part:
                body += extract_email_body(part)
    return body

def fetch_recent_school_emails(query: str = "newer_than:1d") -> List[Dict[str, str]]:
    """Fetches emails matching the query and returns their content."""
    service = get_gmail_service()
    
    # You can expand this query string via environment variables
    # e.g., "from:school.edu OR from:daycare.com newer_than:1d"
    search_query = os.environ.get("GMAIL_SEARCH_QUERY", query)
    
    results = service.users().messages().list(userId='me', q=search_query).execute()
    messages = results.get('messages', [])
    
    parsed_emails = []
    
    for msg in messages:
        msg_data = service.users().messages().get(userId='me', id=msg['id'], format='full').execute()
        
        headers = msg_data['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        date_received = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
        
        body_text = extract_email_body(msg_data['payload'])
        
        parsed_emails.append({
            "subject": subject,
            "sender": sender,
            "date_received": date_received,
            "sender": sender,
            "body": body_text[:2000] # Truncate to save token costs if emails are massive
        })
        
    return parsed_emails