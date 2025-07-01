import os
import hashlib
import requests
import smtplib
import difflib
from email.mime.text import MIMEText

HASH_FILE = "hash.txt"
CONTENT_FILE = "content.txt"

def get_website_html(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error fetching website: {e}")
        return None

def get_website_hash(content):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()

def load_hash():
    if os.path.exists(HASH_FILE):
        with open(HASH_FILE, "r") as f:
            return f.read().strip()
    return None

def save_hash(hash_value):
    with open(HASH_FILE, "w") as f:
        f.write(hash_value)

def load_html():
    if os.path.exists(CONTENT_FILE):
        with open(CONTENT_FILE, "r", encoding="utf-8") as f:
            return f.read()
    return ""

def save_html(html):
    with open(CONTENT_FILE, "w", encoding="utf-8") as f:
        f.write(html)

def get_diff(old, new):
    diff = difflib.unified_diff(
        old.splitlines(), new.splitlines(),
        fromfile='previous', tofile='current', lineterm='', n=3
    )
    diff_lines = list(diff)[:40]  # Limit to first 40 lines
    return '\n'.join(diff_lines) if diff_lines else '(Content changed, but diff is empty)'

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

    # Load previous hash and HTML
    previous_hash = load_hash()
    previous_html = load_html()

    # Fetch current HTML and hash
    current_html = get_website_html(url)
    if current_html is None:
        print("Error: Could not fetch website content.")
        return
    current_hash = get_website_hash(current_html)

    print(f"Previous hash: {previous_hash}")
    print(f"Current hash: {current_hash}")

    if previous_hash != current_hash:
        print("Website has been updated!")
        diff = get_diff(previous_html, current_html)
        email_body = (
            f"The website {url} has been updated.\n\n"
            f"Diff (first 40 lines):\n\n{diff}"
        )
        send_email("Website Updated", email_body, recipient_email)
        print("Email sent!")
        save_html(current_html)
    else:
        print("No changes detected.")

    save_hash(current_hash)

if __name__ == "__main__":
    main()
