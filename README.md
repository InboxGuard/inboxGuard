# InboxGuard - Email Phishing Detection Pipeline

InboxGuard is a pipeline designed to detect phishing emails in Gmail accounts. It automates email extraction, phishing detection using a machine learning model, and Gmail actions (e.g., labeling emails as phishing, suspicious, or safe).

## 🎯 Overview

The pipeline consists of the following components:

1. **Email Extraction**: Extracts emails from a Gmail account using IMAP.
2. **Phishing Detection**: Analyzes emails using a machine learning model to classify them as:
   - **Phishing** (1): Malicious emails attempting to steal information.
   - **Legitimate** (0): Safe emails.
   - **Suspicious** (-1): Emails with uncertain classification.
3. **Gmail Actions**: Labels emails in Gmail based on the classification results.

## 🏗️ Architecture

The pipeline is divided into three services:

1. **Email Service**:

   - Extracts emails from Gmail and saves them as JSON.
   - Located in the `email-service` directory.

2. **Model Service**:

   - A FastAPI-based microservice that uses a machine learning model to classify emails.
   - Located in the `model-service` directory.

3. **Actions Service**:
   - Reads classification results and performs actions on Gmail (e.g., labeling emails).
   - Located in the `actions-service` directory.

## 📁 Project Structure

```plaintext
InboxGuard/
├── email-service/        # Service for extracting emails from Gmail
├── model-service/        # Service for phishing detection (ML model)
├── actions-service/      # Service for labeling emails in Gmail
├── inboxguard.sh         # Shell script to run the pipeline
├── start.py              # Python script to automate the pipeline
├── docker-compose.yml    # Docker Compose configuration
├── Dockerfile            # Dockerfile for the model service
├── .env                  # Environment variables (e.g., Gmail credentials)
└── README.md             # Project documentation
```

## 🚀 Setup Instructions

### Prerequisites

1. **Python 3.11** or higher.
2. **Docker** (optional, for running the model service in a container).
3. **Gmail App Password**:
   - Enable IMAP in your Gmail account settings.
   - Generate an app password if 2FA is enabled.

### Step 1: Clone the Repository

```bash
git clone https://github.com/InboxGuard/inboxGuard
cd inboxGuard
```

### Step 2: Install Dependencies

Option 1: Using Virtual Environment (Recommended)

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 3: Run the Model Service

If you want to run the model service separately, you can use Docker:

```bash
python3 model-service/main.py
```

### Step 5: Make the Pipeline Script Executable

Ensure the inboxguard.sh script is executable by running:

```bash
chmod +x inboxguard.sh
```

### Step 6: Run the Pipeline Script

```bash
./inboxguard.sh -e email@gmail.com -p "your_app_password"
```

## 🛠️ How It Works

### 1. Email Extraction

- The `email-service` extracts emails from Gmail and saves them as JSON files in `email-service/extracted_emails/emails.json`.

### 2. Phishing Detection

- The `model-service` analyzes the extracted emails and saves the classification results as JSON files in `model-service/responses/`.

### 3. Gmail Actions

- The `actions-service` reads the classification results and labels emails in Gmail based on the predictions.

---

## 📊 Classification Results

Classification results are stored in the `model-service/responses/` directory. Each email is classified as:

- **Phishing (1):** Moved to the `Inboxguard/Phishing` label.
- **Suspicious (-1):** Moved to the `Inboxguard/Suspicious` label.
- **Legitimate (0):** Moved to the `Inboxguard/Safe` label.

---

## 📝 Notes

- Ensure IMAP is enabled in your Gmail account.
- Use a Gmail app password for authentication.
- This pipeline is for educational and personal use only. Keep your credentials secure.

## 🛠️ Script Options

The `inboxguard.sh` script supports the following options:

- `-e, --email EMAIL`: Specifies the Gmail address to use for the pipeline.
- `-p, --password PASSWORD`: Specifies the Gmail app password (not the regular Gmail password).
- `-n, --num-emails NUM`: Specifies the number of emails to process (default is 10).
- `-f, --fork`: Executes tasks using child processes (via `fork`).
- `-t, --thread`: Executes tasks using threads for parallel processing.
- `-s, --subshell`: Executes tasks in a subshell (isolated environment).
- `-l, --log DIR`: Specifies a custom directory for logging (default: `/var/log/inboxguard`).
- `-r, --restore`: Resets parameters to default values (requires admin privileges).
- `-h, --help`: Displays the help message with usage instructions.

### Examples

- Run the pipeline with a Gmail account:

  ```bash
  ./inboxguard.sh -e user@gmail.com -p "your_app_password"
  ```

- Process 20 emails:

  ```bash
  ./inboxguard.sh -e user@gmail.com -p "your_app_password" -n 20
  ```

- Use fork mode:

  ```bash
  ./inboxguard.sh -e user@gmail.com -p "your_app_password" -f
  ```

- Specify a custom log directory:

  ```bash
  ./inboxguard.sh -e user@gmail.com -p "your_app_password" -l /tmp/inboxguard_logs
  ```

- Reset parameters to default (requires admin privileges):
  ```bash
  sudo ./inboxguard.sh -r
  ```
