import requests
import hashlib
import logging
import os
import time
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import json

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_website_hash(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for bad responses
        return hashlib.sha256(response.content).hexdigest()
    except requests.RequestException as e:
        logging.error(f"Failed to fetch website content: {e}")
        return None

def authenticate_gmail():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            credentials_json = os.getenv('GOOGLE_CREDENTIALS')
            flow = InstalledAppFlow.from_client_config(json.loads(credentials_json), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def send_email(subject, body, to_email, creds):
    service = build('gmail', 'v1', credentials=creds)

    message = MIMEMultipart()
    message['to'] = to_email
    message['subject'] = subject

    msg_body = MIMEText(body, 'plain')
    message.attach(msg_body)

    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    try:
        message = service.users().messages().send(userId="me", body={'raw': raw_message}).execute()
        logging.info(f"Email sent! Message Id: {message['id']}")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

def main():
    url = os.getenv('URL')
    recipient_email = os.getenv('RECIPIENT_EMAIL')

    if not all([url, recipient_email]):
        logging.error("Missing required environment variables")
        return

    creds = authenticate_gmail()
    if not creds:
        logging.error("Authentication failed. Exiting.")
        return

    previous_hash = get_website_hash(url)
    if previous_hash is None:
        logging.error("Initial hash could not be computed. Exiting.")
        return
    logging.info(f"Initial hash: {previous_hash}")

    while True:
        time.sleep(600)  # Check every 10 minutes
        current_hash = get_website_hash(url)
        if current_hash is None:
            logging.error("Current hash could not be computed. Skipping this iteration.")
            continue
        logging.info(f"Current hash: {current_hash}")

        if current_hash != previous_hash:
            send_email("Website Updated", f"The website {url} has been updated.", recipient_email, creds)
            logging.info("Email sent!")
            previous_hash = current_hash

if __name__ == "__main__":
    main()
