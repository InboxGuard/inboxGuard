# Gmail POP3 Email Extractor (Python)

## Overview

A Python script to securely connect to Gmail via POP3 over SSL, retrieve recent emails, extract key details (sender, receiver, subject, date, body), and export them as structured JSON. The script also logs operations and saves raw email files for debugging.

## Features

- Secure POP3 SSL connection to Gmail
- Supports interactive prompts or environment variables for credentials and settings
- Decodes email headers and handles various encodings
- Extracts and decodes email bodies, including multipart and base64 content
- Outputs all extracted emails as JSON
- Logs operations and errors for traceability
- Checks for required dependencies

## How It Works

1. **Setup:** Creates output, log, and temp directories; configures logging
2. **Dependency Check:** Verifies required Python modules
3. **User Input:** Prompts for Gmail address, app password, and email count, or loads from environment variables
4. **POP3 Connection:** Connects to Gmail POP3 server with SSL and credentials
5. **Email Retrieval:** Fetches the most recent emails; saves raw `.eml` files
6. **Parsing:** Extracts and decodes headers and body, handling multipart and encoded content
7. **JSON Output:** Writes parsed emails to a JSON file
8. **Cleanup:** Removes temp files; displays summary and JSON preview

## Configuration

You can use a `.env` file to set sensitive information and avoid interactive prompts. Create a `.env` file in the project directory:

```env
GMAIL_ADDRESS=your_gmail_address@gmail.com
GMAIL_APP_PASSWORD=your_app_password
EMAIL_COUNT=10
```

Install `python-dotenv` if you want to use environment variables:

```sh
pip install python-dotenv
```

## Usage

1. Run the script:  
   `python extract_gmail.py`
2. Enter your Gmail address and app password when prompted, or set them in the `.env` file  
   (Enable POP3 in Gmail settings and use an app password if 2FA is enabled)
3. Specify the number of emails to extract (default: 10)
4. Output directory will include:

- `emails.json` (extracted emails)
- `extraction.log` (log file)
- `email_raw_*.eml` (raw emails for debugging)

## Requirements

- Python 3.x
- Standard libraries: `poplib`, `email`, `json`, `os`, `logging`
- Optional: `python-dotenv`
- Internet connection

## Notes

- Enable POP3 in your Gmail account settings
- Use an app password if 2FA is enabled
- For educational/personal use only; keep credentials secure
- Review and adapt the script as needed for your environment
