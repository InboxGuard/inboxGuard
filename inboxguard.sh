#!/bin/bash

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Required Options:"
    echo "  -h, --help               Show this help message"
    echo "  -f, --fork               Execute tasks using fork"
    echo "  -t, --threads            Execute tasks using threads"
    echo "  -s, --subshell           Execute tasks in a subshell"
    echo "  -l, --log-dir DIR        Specify a directory for logging"
    echo "  -r, --reset              Reset parameters to default (requires admin privileges)"
    echo ""
    echo "Project-specific Options:"
    echo "  -e, --email EMAIL        Gmail address"
    echo "  -p, --password PASSWORD  Gmail app password (use quotes if it contains spaces)"
    echo "  -n, --num-emails NUM     Number of emails to process (default: 10)"
    echo ""
    echo "Examples:"
    echo "  $0 -h"
    echo "  $0 -f -e user@gmail.com -p \"your app password\""
    echo "  $0 -t --email user@gmail.com --password \"your app password\" --num-emails 20"
    echo "  $0 -s -l /custom/log/dir -e user@gmail.com -p \"password\""
    echo ""
    echo "Note: Use Gmail App Password, not your regular password"
    echo "      If password contains spaces, wrap it in quotes"
}

# Default values
NUM_EMAILS=10
EMAIL=""
PASSWORD=""
EXECUTION_MODE=""
CUSTOM_LOG_DIR=""
RESET_PARAMS=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -h|--help)
            show_usage
            exit 0
            ;;
        -f|--fork)
            EXECUTION_MODE="fork"
            shift
            ;;
        -t|--threads)
            EXECUTION_MODE="threads"
            shift
            ;;
        -s|--subshell)
            EXECUTION_MODE="subshell"
            shift
            ;;
        -l|--log-dir)
            CUSTOM_LOG_DIR="$2"
            shift 2
            ;;
        -r|--reset)
            RESET_PARAMS=true
            shift
            ;;
        -e|--email)
            EMAIL="$2"
            shift 2
            ;;
        -p|--password)
            PASSWORD="$2"
            shift 2
            ;;
        -n|--num-emails)
            NUM_EMAILS="$2"
            shift 2
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Handle reset option (requires admin privileges)
if [[ "$RESET_PARAMS" == true ]]; then
    print_status "🔄 Resetting parameters to default..."
    if [[ $EUID -ne 0 ]]; then
        print_error "Reset option requires admin privileges. Please run with sudo."
        exit 1
    fi
    # Reset to default values
    NUM_EMAILS=10
    EMAIL=""
    PASSWORD=""
    EXECUTION_MODE=""
    CUSTOM_LOG_DIR=""
    print_success "Parameters reset to default values."
    exit 0
fi

# Set default execution mode if none specified
if [[ -z "$EXECUTION_MODE" ]]; then
    EXECUTION_MODE="subshell"
    print_warning "No execution mode specified, defaulting to subshell mode"
    log_message "WARNING" "No execution mode specified, defaulting to subshell mode"
fi

# Validate required arguments
if [[ -z "$EMAIL" || -z "$PASSWORD" ]]; then
    print_error "Email and password are required!"
    show_usage
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Define the .env file path
ENV_FILE="$SCRIPT_DIR/.env"

# Log pipeline steps and outputs
if [[ -n "$CUSTOM_LOG_DIR" ]]; then
    LOG_DIR="$CUSTOM_LOG_DIR"
    print_status "📁 Using custom log directory: $LOG_DIR"
else
    LOG_DIR="$SCRIPT_DIR/logs"
fi
mkdir -p "$LOG_DIR"

# Update the pipeline log file path to be in the logs directory
PIPELINE_LOG_FILE="$LOG_DIR/pipeline.log"

log_message() {
    local level="$1"
    shift
    local message="$@"
    local timestamp
    timestamp="$(date +"%Y-%m-%d %H:%M:%S")"
    echo -e "$timestamp [$level] $message" >> "$PIPELINE_LOG_FILE"
}

print_status "🚀 Starting InboxGuard Pipeline..."
log_message "INFOS" "🚀 Starting InboxGuard Pipeline..."
print_status "Email: $EMAIL"
log_message "INFOS" "Email: $EMAIL"
print_status "Number of emails: $NUM_EMAILS"
log_message "INFOS" "Number of emails: $NUM_EMAILS"
print_status "Execution mode: $EXECUTION_MODE"
log_message "INFOS" "Execution mode: $EXECUTION_MODE"
print_status "Log directory: $LOG_DIR"
log_message "INFOS" "Log directory: $LOG_DIR"

# Create or update .env file
print_status "📝 Creating environment file..."
log_message "INFOS" "📝 Creating environment file..."
cat > "$ENV_FILE" << EOF
GMAIL_ADDRESS=$EMAIL
GMAIL_PASSWORD=$PASSWORD
NUM_EMAILS=$NUM_EMAILS
EOF
log_message "SUCCESS" "Environment file created at $ENV_FILE"

# Functions for different execution modes
execute_with_fork() {
    print_status "🍴 Executing pipeline using fork..."
    log_message "INFOS" "🍴 Executing pipeline using fork..."
    python3 start.py &
    wait $!
    return $?
}

execute_with_threads() {
    print_status "🧵 Executing pipeline using threads..."
    log_message "INFOS" "🧵 Executing pipeline using threads..."
    # Note: Python handles threading internally, but we can use background execution
    python3 start.py &
    PYTHON_PID=$!
    wait $PYTHON_PID
    return $?
}

execute_with_subshell() {
    print_status "🐚 Executing pipeline in subshell..."
    log_message "INFOS" "🐚 Executing pipeline in subshell..."
    (python3 start.py)
    return $?
}

# Run the Python pipeline with selected execution mode
print_status "🐍 Starting Python pipeline..."
log_message "INFOS" "🐍 Starting Python pipeline..."

case "$EXECUTION_MODE" in
    "fork")
        execute_with_fork
        PIPELINE_EXIT_CODE=$?
        ;;
    "threads")
        execute_with_threads
        PIPELINE_EXIT_CODE=$?
        ;;
    "subshell")
        execute_with_subshell
        PIPELINE_EXIT_CODE=$?
        ;;
    *)
        print_error "Invalid execution mode: $EXECUTION_MODE"
        exit 1
        ;;
esac

if [[ $PIPELINE_EXIT_CODE -eq 0 ]]; then
    print_success "🎉 InboxGuard pipeline completed successfully!"
    log_message "SUCCESS" "🎉 InboxGuard pipeline completed successfully!"
    print_status "Check the logs in each service directory for detailed information."
else
    print_error "❌ Pipeline failed!"
    log_message "ERROR" "❌ Pipeline failed!"
    exit 1
fi

# Log email extraction step
log_message "INFOS" "📧 Step 1: Extracting emails..."

# Log model service step
log_message "INFOS" "🤖 Step 2: Processing with AI model..."

# Log Gmail actions step
log_message "INFOS" "🏷️ Step 4: Creating Gmail labels..."

# Log email actions step
log_message "INFOS" "⚡ Step 5: Applying email actions..."

# Ensure Gmail processor logs are saved in the correct directory
GMAIL_PROCESSOR_LOG_DIR="$SCRIPT_DIR/logs"
if [[ ! -d "$GMAIL_PROCESSOR_LOG_DIR" ]]; then
    mkdir -p "$GMAIL_PROCESSOR_LOG_DIR"
fi

# Update the log file path for Gmail processor
GMAIL_PROCESSOR_LOG_FILE="$GMAIL_PROCESSOR_LOG_DIR/gmail_processor_$(date '+%Y%m%d_%H%M%S').log"
log_message "INFOS" "Log file saved to: $GMAIL_PROCESSOR_LOG_FILE"

# Redirect all terminal output to the pipeline log file
exec > >(tee -a "$PIPELINE_LOG_FILE") 2>&1

# Ensure the pipeline log file is created in the logs directory
if [[ ! -f "$PIPELINE_LOG_FILE" ]]; then
    touch "$PIPELINE_LOG_FILE"
fi