import imaplib
import email
import os  # Add missing import
from email.header import decode_header

def connect_to_gmail(EMAIL, password):
    """Connect to Gmail IMAP server"""
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(EMAIL, password)
    return mail

def label_exists(mail, label_name):
    """Check if a label exists"""
    status, folders = mail.list()
    if status != 'OK':
        return False
    
    label_name = label_name.lower()
    for folder in folders:
        # Decode folder name which might be encoded
        decoded = decode_header(folder.decode().split(' "/" ')[-1])
        current_label = str(decoded[0][0]).lower()
        if current_label == label_name:
            return True
    return False

def create_label(mail, label_name):
    """Attempt to create a label by creating an IMAP folder"""
    try:
        # Try to create the folder (which Gmail may interpret as a label)
        status, response = mail.create(label_name)
        if status == 'OK':
            print(f"Label '{label_name}' created successfully")
            return True
        else:
            print(f"Failed to create label: {response[0].decode()}")
            return False
    except Exception as e:
        print(f"Error creating label: {str(e)}")
        return False

def ensure_label_exists(mail, label_name):
    """Check if label exists, create if it doesn't"""
    if not label_exists(mail, label_name):
        print(f"Label '{label_name}' not found, attempting to create...")
        return create_label(mail, label_name)
    print(f"Label '{label_name}' already exists")
    return True

def main():
    # 1. Load .env from parent directory (InboxGuard)
    env = {}
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            if "=" in line and not line.startswith("#"):
                k, v = line.strip().split("=", 1)
                env[k] = v
    # Replace with your credentials
    EMAIL = env.get("GMAIL_ADDRESS")
    PASSWORD = env.get("GMAIL_PASSWORD")

    if not EMAIL or not PASSWORD:
        print("Missing credentials in .env")
        return
    
    mail = connect_to_gmail(EMAIL, PASSWORD)
    
    try:
        # Labels you want to ensure exist
        labels_to_create = ['Inboxguard', 'Inboxguard/Phishing', 'Inboxguard/Suspicious', 'Inboxguard/Safe']

        for label in labels_to_create:
            # Note: Sublabels might not work reliably via IMAP
            if ensure_label_exists(mail, label):
                print(f"Success with label: {label}")
            else:
                print(f"Failed with label: {label}")
                
    finally:
        mail.logout()

if __name__ == '__main__':
    main()