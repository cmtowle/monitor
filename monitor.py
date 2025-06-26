import os
import hashlib
import requests

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

def main():
    """
    Main function to monitor the website and send email if updated.
    """
    url = os.getenv("URL")
    recipient_email = os.getenv("RECIPIENT_EMAIL")

    if not url or not recipient_email:
        print("Error: Missing URL or recipient email.")
        return

    # Load previous hash from hash.txt
    previous_hash = load_hash()
    print(f"Previous hash: {previous_hash}")

    # Compute the current hash of the website
    current_hash = get_website_hash(url)
    if current_hash is None:
        print("Error: Could not compute hash for the website.")
        return
    print(f"Current hash: {current_hash}")

    # Compare hashes and notify if there are changes
    if previous_hash != current_hash:
        print("Website has been updated!")
        # Add email notification logic here (if needed)
    else:
        print("No changes detected.")

    # Save the current hash to hash.txt
    save_hash(current_hash)

if __name__ == "__main__":
    main()
