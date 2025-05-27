import os
import sys
import poplib
import email
from email.header import decode_header
from datetime import datetime
import json

# 1. Load .env
env = {}
with open(".env") as f:
    for line in f:
        if "=" in line and not line.startswith("#"):
            k, v = line.strip().split("=", 1)
            env[k] = v

EMAIL = env.get("GMAIL_ADDRESS")
PASSWORD = env.get("GMAIL_PASSWORD")

if not EMAIL or not PASSWORD:
    print("Missing credentials in .env")
    sys.exit(1)

# 2. Prepare output directory
folder = datetime.now().strftime("%Y-%m-%d_%H")
os.makedirs(folder, exist_ok=True)
json_file = os.path.join(folder, "emails.json")

# 3. Connect to POP3
server = poplib.POP3_SSL("pop.gmail.com", 995)
server.user(EMAIL)
server.pass_(PASSWORD)
total = len(server.list()[1])
emails = []

def decode_mime(s):
    if not s:
        return ""
    decoded = decode_header(s)
    result = ""
    for part, enc in decoded:
        if isinstance(part, bytes):
            result += part.decode(enc or "utf-8", errors="replace")
        else:
            result += part
    return result

for i in range(1, total + 1):
    resp, lines, octets = server.retr(i)
    raw_msg = b"\r\n".join(lines)
    msg = email.message_from_bytes(raw_msg)

    sender = decode_mime(msg.get("From", ""))
    subject = decode_mime(msg.get("Subject", ""))
    body = ""

    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain" and "attachment" not in str(part.get("Content-Disposition", "")):
                charset = part.get_content_charset() or "utf-8"
                try:
                    body = part.get_payload(decode=True).decode(charset, errors="replace")
                except:
                    pass
                break
    else:
        try:
            body = msg.get_payload(decode=True).decode(msg.get_content_charset() or "utf-8", errors="replace")
        except:
            pass

    emails.append({
        "id": str(i),
        "sender": sender,
        "subject": subject,
        "body": body.strip()
    })

# 4. Save to JSON
with open(json_file, "w") as f:
    json.dump(emails, f, ensure_ascii=False, indent=2)

print(f"✅ Saved {len(emails)} emails to {json_file}")
