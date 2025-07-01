import os
import hashlib
import requests
import smtplib
from email.mime.text import MIMEText

def get_website_hash(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return hashlib.sha256(response.content).hexdigest()
    except requests.RequestException as e:
        print(f"Error fetching website: {e}")
        return None

def load_hash():
    if os.path.exists("hash.txt"):
        with open("hash.txt", "r") as f:
            return f.read().strip()
    return None

def save_hash(hash_value):
    with open("hash.txt", "w") as f:
        f.write(hash_value)

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
    url = os.getenv("URL")
    recipient_email = os.getenv("RECIPIENT_EMAIL")

    if not url or not recipient_email:
        print("Error: Missing URL or recipient email.")
        return

    previous_hash = load_hash()
    print(f"Previous hash: {previous_hash}")

    current_hash = get_website_hash(url)
    if current_hash is None:
        print("Error: Could not compute hash for the website.")
        return
    print(f"Current hash: {current_hash}")

    if previous_hash != current_hash:
        print("Website has been updated!")
        send_email("Website Updated", f"The website {url} has been updated.", recipient_email)
        print("Email sent!")
    else:
        print("No changes detected.")

    save_hash(current_hash)

if __name__ == "__main__":
    main()
