import requests
import hashlib
import os

def get_website_hash(url):
    """
    Fetch the content of the website and compute its hash.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return hashlib.sha256(response.content).hexdigest()
    except requests.RequestException as e:
        print(f"Error fetching website: {e}")
        return None

def load_hash():
    """
    Load the hash from a file if it exists.
    """
    if os.path.exists("hash.txt"):
        with open("hash.txt", "r") as f:
            return f.read().strip()
    return None

def save_hash(hash_value):
    """
    Save the hash to a file.
    """
    with open("hash.txt", "w") as f:
        f.write(hash_value)

def send_email(subject, body, to_email):
    """
    Send an email using Gmail SMTP.
    """
    from_email = os.getenv('GMAIL_ADDRESS')
    app_password = os.getenv('GMAIL_APP_PASSWORD')

    # Ensure the secrets are properly set
    if not from_email or not app_password:
        print("Error: Missing Gmail credentials.")
        return

    from email.mime.text import MIMEText
    import smtplib

    # Create the email message
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    try:
        # Connect to Gmail SMTP server
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(from_email, app_password)
            smtp.sendmail(from_email, [to_email], msg.as_string())
        print("Email sent successfully!")
    except Exception as e:
        print(f"Error sending email: {e}")

def main():
    """
    Main function to monitor the website and send email if updated.
    """
    # Load environment variables
    url = os.getenv('URL')
    recipient_email = os.getenv('RECIPIENT_EMAIL')

    if not url or not recipient_email:
        print("Error: Missing URL or recipient email.")
        return

    # Load the previous hash
    previous_hash = load_hash()
    print(f"Previous hash: {previous_hash}")

    # Compute the current hash
    current_hash = get_website_hash(url)
    if current_hash is None:
        print("Error: Could not compute hash for the website.")
        return
    print(f"Current hash: {current_hash}")

    # Compare hashes and send email if there's a change
    if previous_hash != current_hash:
        print("Website has been updated!")
        send_email(
            subject="Website Updated",
            body=f"The website {url} has been updated.",
            to_email=recipient_email
        )
        # Save the new hash
        save_hash(current_hash)
    else:
        print("No changes detected.")

if __name__ == "__main__":
    main()
