import imaplib
import email
from email.header import decode_header
from datetime import datetime
import json
import os
import sys

# 1. Load .env from parent directory (InboxGuard)
env = {}
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
with open(env_path, encoding='utf-8') as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            k, v = line.strip().split("=", 1)
            env[k] = v
  
EMAIL = env.get("GMAIL_ADDRESS")
PASSWORD = env.get("GMAIL_PASSWORD")
NUM_EMAILS = int(env.get("NUM_EMAILS", 10))

if not EMAIL or not PASSWORD:
    print("Missing credentials in .env")
    sys.exit(1)

# 2. Prepare output directory in email-service folder
folder = "extracted_emails"
os.makedirs(folder, exist_ok=True)
json_file = os.path.join(folder, "emails.json")

# 3. Connect to IMAP
try:
    mail = imaplib.IMAP4_SSL('imap.gmail.com', 993)
    mail.login(EMAIL, PASSWORD)
    mail.select('inbox')
    
    # Search for all emails
    status, messages = mail.search(None, 'ALL')
    mail_ids = messages[0].split()
    
    # Get the most recent emails (limit by NUM_EMAILS)
    recent_mail_ids = mail_ids[-NUM_EMAILS:] if len(mail_ids) > NUM_EMAILS else mail_ids
    
    emails = []
    
    def decode_mime(s):
        if not s:
            return ""
        decoded = decode_header(s)
        result = ""
        for decoded_part, enc in decoded:
            if isinstance(decoded_part, bytes):
                result += decoded_part.decode(enc or 'utf-8', errors='ignore')
            else:
                result += decoded_part
        return result
    
    def get_email_body(msg):
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    try:
                        body += part.get_payload(decode=True).decode('utf-8', errors='ignore')
                    except:
                        body += str(part.get_payload())
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(msg.get_payload())
        return body
    
    for mail_id in recent_mail_ids:
        status, msg_data = mail.fetch(mail_id, '(RFC822)')
        msg = email.message_from_bytes(msg_data[0][1])
        
        # Get UID
        status, uid_data = mail.fetch(mail_id, '(UID)')
        uid = uid_data[0].decode().split()[2].rstrip(')')
        
        sender = decode_mime(msg.get("From", ""))
        subject = decode_mime(msg.get("Subject", ""))
        date = msg.get("Date", "")
        body = get_email_body(msg)
        
        emails.append({
            "uid": uid,
            "sender": sender,
            "subject": subject,
            "date": date,
            "body": body
        })
        
        print(f"✓ Extracted email {len(emails)}/{len(recent_mail_ids)}: {subject[:50]}...")
    
    mail.close()
    mail.logout()
    
    # 4. Save to JSON
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(emails, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Saved {len(emails)} emails to {json_file}")
    
    # Don't auto-trigger batch processing - let the pipeline handle it
    print("📧 Email extraction completed successfully")

except imaplib.IMAP4.error as e:
    print(f"IMAP error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

print("🎯 Email service finished")