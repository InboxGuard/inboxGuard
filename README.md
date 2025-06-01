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

### Core Options

- `-e, --email EMAIL`: Specifies the Gmail address to use for the pipeline.
- `-p, --password PASSWORD`: Specifies the Gmail app password (not the regular Gmail password).
- `-n, --num-emails NUM`: Specifies the number of emails to process (default is 10).
- `-h, --help`: Displays the help message with usage instructions.

### Execution Mode Options

The script supports three different execution modes, each with specific use cases:

- `-f, --fork`: Executes tasks using child processes (via `fork`).
- `-t, --threads`: Executes tasks using threads for parallel processing.
- `-s, --subshell`: Executes tasks in a subshell (isolated environment). **[Default]**

### Utility Options

- `-l, --log-dir DIR`: Specifies a custom directory for logging (default: `./logs`).
- `-r, --reset`: Resets parameters to default values (requires admin privileges).

## 🔄 Execution Modes Explained

### Why Different Execution Modes?

Different execution modes provide flexibility for various deployment scenarios and system requirements:

### 🍴 Fork Mode (`-f`)

**What it does**: Creates a separate child process to run the pipeline.

**When to use**:

- When you need process isolation for security
- For production environments where process crashes shouldn't affect the parent
- When running multiple pipelines simultaneously

**Advantages**:

- Complete process isolation
- Memory is not shared between processes
- If the pipeline crashes, it won't affect the main script

**Disadvantages**:

- Higher memory usage (separate process)
- Slightly slower startup time
- Inter-process communication overhead

### 🧵 Threads Mode (`-t`)

**What it does**: Executes the pipeline in a background thread while maintaining shared memory space.

**When to use**:

- For better resource utilization
- When you need shared state between the main script and pipeline
- For faster execution with shared memory access

**Advantages**:

- Lower memory footprint (shared memory)
- Faster inter-thread communication
- Better for concurrent operations

**Disadvantages**:

- Less isolation (threads share memory)
- Potential for memory leaks affecting the entire process
- Threading complexity in Python (GIL limitations)

### 🐚 Subshell Mode (`-s`) - **Default**

**What it does**: Runs the pipeline in an isolated shell environment.

**When to use**:

- For development and testing (recommended default)
- When you need environment variable isolation
- For simple, straightforward execution

**Advantages**:

- Environment isolation (variables, working directory)
- Simple and reliable execution model
- Clean separation of execution context
- Default choice for most use cases

**Disadvantages**:

- Less control over the execution process
- Limited inter-process communication options

### Examples

- **Basic usage** (uses default subshell mode):

  ```bash
  ./inboxguard.sh -e user@gmail.com -p "your_app_password"
  ```

- **Process 20 emails with fork mode**:

  ```bash
  ./inboxguard.sh -f -e user@gmail.com -p "your_app_password" -n 20
  ```

- **Use threads mode for better performance**:

  ```bash
  ./inboxguard.sh -t -e user@gmail.com -p "your_app_password"
  ```

- **Explicit subshell mode with custom log directory**:

  ```bash
  ./inboxguard.sh -s -e user@gmail.com -p "your_app_password" -l /tmp/inboxguard_logs
  ```

- **Reset parameters to default** (requires admin privileges):
  ```bash
  sudo ./inboxguard.sh -r
  ```

## 🎯 Choosing the Right Execution Mode

| Scenario                 | Recommended Mode | Reason                              |
| ------------------------ | ---------------- | ----------------------------------- |
| **Development/Testing**  | `-s` (subshell)  | Simple, isolated, reliable          |
| **Production/Security**  | `-f` (fork)      | Process isolation, crash protection |
| **Performance Critical** | `-t` (threads)   | Shared memory, faster execution     |
| **Multiple Pipelines**   | `-f` (fork)      | Independent processes               |
| **Resource Constrained** | `-t` (threads)   | Lower memory usage                  |

---

## ✅ Implementation Status

### Step 3: Logging Implementation - COMPLETED

**Objective**: Add a logging mechanism to redirect standard output and errors to `/var/log/inboxguard/history.log`.

**Status**: ✅ **SUCCESSFULLY COMPLETED**

#### Key Achievements:

- ✅ Centralized logging to `/var/log/inboxguard/history.log`
- ✅ Standardized format: `yyyy-mm-dd-hh-mm-ss : username : LEVEL : message`
- ✅ Automatic file creation and permission handling
- ✅ Multi-user support with username tracking
- ✅ Comprehensive error tracking and session management
- ✅ Signal handling for script interruptions
- ✅ Integration with existing pipeline components

#### Technical Implementation:

- Enhanced all print functions to log to centralized location
- Added `setup_logging()` and `write_to_history_log()` functions
- Implemented permission handling for both root and non-root users
- Added signal handlers and cleanup functions
- Maintains backward compatibility with existing logging

---

## 📋 Logging System

InboxGuard features a comprehensive logging system that tracks all pipeline activities and redirects output to a centralized location for easy monitoring and troubleshooting.

### 🎯 Logging Overview

The logging system provides:

- **Centralized logging** to `/var/log/inboxguard/history.log`
- **Standardized format** for all log entries
- **Multi-user support** with username tracking
- **Session management** with start/end logging
- **Error tracking** with exit codes
- **Automatic setup** with permission handling

### 📝 Log Format

All log entries follow this standardized format:

```
yyyy-mm-dd-hh-mm-ss : username : LEVEL : message
```

**Components:**

- `yyyy-mm-dd-hh-mm-ss`: Timestamp (e.g., 2025-06-01-14-30-45)
- `username`: System username running the script (from `whoami`)
- `LEVEL`: Either `INFOS` for informational messages or `ERROR` for error messages
- `message`: The actual log message content

### 📂 Log Location

- **Directory**: `/var/log/inboxguard/`
- **File**: `/var/log/inboxguard/history.log`
- **Permissions**:
  - Directory: 755 (drwxr-xr-x)
  - File: 644 (rw-rw-r--)

### 🚀 Automatic Setup

The logging system automatically:

1. **Creates log directory** if it doesn't exist
2. **Handles permissions** using sudo when necessary
3. **Sets up file permissions** for multi-user access
4. **Initializes logging** on script startup

### 📊 Sample Log Output

#### Successful Execution

```
2025-06-01-14-30-45 : admin : INFOS : InboxGuard script started with user: admin
2025-06-01-14-30-45 : admin : INFOS : Script arguments: -e test@gmail.com -p password -f
2025-06-01-14-30-45 : admin : INFOS : Email: test@gmail.com
2025-06-01-14-30-45 : admin : INFOS : Number of emails: 10
2025-06-01-14-30-45 : admin : INFOS : Execution mode: fork
2025-06-01-14-30-46 : admin : INFOS : 🚀 Starting InboxGuard Pipeline...
2025-06-01-14-31-20 : admin : INFOS : 🎉 InboxGuard pipeline completed successfully!
2025-06-01-14-31-20 : admin : INFOS : InboxGuard script session ended
```

#### Error Scenarios

```
2025-06-01-14-31-20 : admin : ERROR : Email and password are required!
2025-06-01-14-31-20 : admin : ERROR : Script terminated with exit code 1
2025-06-01-14-31-20 : admin : INFOS : InboxGuard script session ended
```

#### Script Interruption

```
2025-06-01-14-32-10 : admin : ERROR : Script interrupted by user
2025-06-01-14-32-10 : admin : INFOS : InboxGuard script session ended
```

### 🔧 Logging Features

#### Core Features

- **Session Tracking**: Logs script start, arguments, and completion
- **Error Handling**: Comprehensive error logging with exit codes
- **Signal Handling**: Captures interruptions (Ctrl+C) and logs them
- **Permission Management**: Handles both root and non-root execution
- **Dual Output**: Maintains both console output and centralized logging

#### Advanced Features

- **Multi-user Support**: Tracks which user ran the script
- **ANSI Color Removal**: Clean log entries without terminal color codes
- **Pipeline Integration**: Works alongside existing pipeline logging
- **Backward Compatibility**: Doesn't interfere with existing log files

### 📋 Viewing Logs

#### View Recent Entries

```bash
tail -10 /var/log/inboxguard/history.log
```

#### View Logs for Specific User

```bash
grep ": username :" /var/log/inboxguard/history.log
```

#### View Error Entries Only

```bash
grep "ERROR" /var/log/inboxguard/history.log
```

#### Follow Logs in Real-time

```bash
tail -f /var/log/inboxguard/history.log
```

### 🛠️ Troubleshooting Logging

#### Permission Issues

If you encounter permission errors:

1. Run the script with `sudo` for initial setup:
   ```bash
   sudo ./inboxguard.sh -e your@gmail.com -p "password"
   ```
2. Or manually create the directory:
   ```bash
   sudo mkdir -p /var/log/inboxguard
   sudo chmod 755 /var/log/inboxguard
   ```

#### Log File Not Created

If the log file is not created:

1. Check if the directory exists and is writable
2. Verify sudo access is available
3. Check disk space in `/var/log/`

#### Checking Log File Status

```bash
# Check if log directory exists
ls -la /var/log/inboxguard/

# Check log file permissions
ls -la /var/log/inboxguard/history.log

# Check disk space
df -h /var/log
```

### 🔄 Log Management

#### Log File Size

Monitor log file size periodically:

```bash
du -h /var/log/inboxguard/history.log
```

#### Manual Log Rotation (if needed)

```bash
# Backup current log
sudo cp /var/log/inboxguard/history.log /var/log/inboxguard/history.log.backup

# Clear current log
sudo truncate -s 0 /var/log/inboxguard/history.log
```

### 🎯 Integration with Pipeline

The logging system is fully integrated with the InboxGuard pipeline and logs:

- **Email extraction** progress and results
- **Model service** processing status
- **Gmail actions** execution and results
- **Script execution** modes and parameters
- **Error conditions** and recovery attempts

All pipeline components now contribute to the centralized log, making debugging and monitoring much easier.

---
