import requests
import hashlib
import os
import smtplib
from email.mime.text import MIMEText

def get_website_hash(url):
    response = requests.get(url)
    response.raise_for_status()
    return hashlib.sha256(response.content).hexdigest()

def send_email(subject, body, to_email):
    from_email = os.getenv('GMAIL_ADDRESS')
    app_password = os.getenv('GMAIL_APP_PASSWORD')
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(from_email, app_password)
        smtp.sendmail(from_email, [to_email], msg.as_string())

def main():
    url = os.getenv('URL')
    recipient_email = os.getenv('RECIPIENT_EMAIL')

    previous_hash = 'db197829b76b384ab56af895e5b2081f8111c35c57d4148c42c6c3d39a1a7907'
    print(f"Initial hash: {previous_hash}")

    # For GitHub Actions, just run once
    current_hash = get_website_hash(url)
    print(f"Current hash: {current_hash}")

    if current_hash != previous_hash:
        send_email("Website Updated", f"The website {url} has been updated.", recipient_email)
        print("Email sent!")
    else:
        print("No change detected.")

if __name__ == "__main__":
    main()
