# Gmail POP3 Email Extractor Script (Python)

## Overview

This Python script connects to a Gmail account via POP3 over SSL, retrieves recent emails, extracts key details (sender, receiver, subject, date, body), and exports them to a JSON file. It also logs the process and saves raw email files for debugging.

## Features

- Secure POP3 SSL connection to Gmail.
- Prompts for Gmail address, app password, and number of emails.
- Decodes email headers (From, To, Subject, Date) and handles various encodings.
- Extracts and decodes email bodies, including multipart and base64 content.
- Outputs structured JSON with all extracted emails.
- Logs operations and errors for traceability.
- Checks for required dependencies (`poplib`, `email`, `json`).

## Workflow

1. **Setup:** Creates output, log, and temp directories; configures logging.
2. **Dependency Check:** Verifies required Python modules.
3. **User Input:** Prompts for Gmail address, app password, and email count.
4. **POP3 Connection:** Connects to Gmail POP3 server with SSL and credentials; handles errors.
5. **Email Retrieval:** Lists and fetches the most recent emails; saves raw `.eml` files.
6. **Parsing:** Extracts and decodes headers and body; handles multipart and encoded content.
7. **JSON Output:** Writes parsed emails to a JSON file.
8. **Cleanup:** Removes temp files; displays summary and JSON preview.

## Environment Configuration

You can configure sensitive information using environment variables instead of interactive prompts. Create a `.env` file in the project directory with the following content:

```env
GMAIL_ADDRESS=your_gmail_address@gmail.com
GMAIL_APP_PASSWORD=your_app_password
EMAIL_COUNT=10
```

The script will automatically load these variables if present. Install the `python-dotenv` package if needed:

```sh
pip install python-dotenv
```

## Usage

1. Run: `python extract_gmail.py`
2. Enter your Gmail address and app password when prompted, or set them in the `.env` file.  
   (Enable POP3 in Gmail settings and use an app password if 2FA is enabled.)
3. Specify the number of emails to extract (default: 10).
4. Output directory will contain:

- `emails.json` (extracted emails)
- `extraction.log` (log file)
- `email_raw_*.eml` (raw emails for debugging)

## Requirements

- Python 3.x
- Standard libraries: `poplib`, `email`, `json`, `os`, `logging`
- Optional: `python-dotenv` for environment variable support
- Internet connection

## Notes

- Enable POP3 in your Gmail account settings.
- Use an app password if 2FA is enabled.
- Intended for educational/personal use; keep credentials secure.
- Review and adapt the script for your environment.
