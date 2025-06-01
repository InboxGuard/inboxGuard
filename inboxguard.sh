#!/bin/bash

set -e  # Exit on any error

# Error handling and cleanup
cleanup() {
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        write_to_history_log "ERROR" "Script terminated with exit code $exit_code"
    fi
    write_to_history_log "INFOS" "InboxGuard script session ended"
}

# Set up signal handlers
trap cleanup EXIT
trap 'write_to_history_log "ERROR" "Script interrupted by user"; exit 130' INT TERM

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Global logging configuration
HISTORY_LOG_DIR="/var/log/inboxguard"
HISTORY_LOG_FILE="$HISTORY_LOG_DIR/history.log"
CURRENT_USER=$(whoami)

# Function to setup logging infrastructure
setup_logging() {
    # Create log directory if it doesn't exist
    if [[ ! -d "$HISTORY_LOG_DIR" ]]; then
        if [[ $EUID -eq 0 ]]; then
            mkdir -p "$HISTORY_LOG_DIR"
            chmod 755 "$HISTORY_LOG_DIR"
        else
            # If not root, try to create with sudo
            if command -v sudo >/dev/null 2>&1; then
                print_status "Creating log directory $HISTORY_LOG_DIR (requires sudo)..."
                sudo mkdir -p "$HISTORY_LOG_DIR"
                sudo chmod 755 "$HISTORY_LOG_DIR"
                sudo chown root:admin "$HISTORY_LOG_DIR" 2>/dev/null || sudo chown root:wheel "$HISTORY_LOG_DIR" 2>/dev/null || true
            else
                print_error "Cannot create log directory $HISTORY_LOG_DIR. Please run with sudo or create manually."
                exit 1
            fi
        fi
    fi
    
    # Create log file if it doesn't exist
    if [[ ! -f "$HISTORY_LOG_FILE" ]]; then
        if [[ $EUID -eq 0 ]]; then
            touch "$HISTORY_LOG_FILE"
            chmod 644 "$HISTORY_LOG_FILE"
        else
            # If not root, try to create with sudo
            if command -v sudo >/dev/null 2>&1; then
                sudo touch "$HISTORY_LOG_FILE"
                sudo chmod 644 "$HISTORY_LOG_FILE"
                sudo chown root:admin "$HISTORY_LOG_FILE" 2>/dev/null || sudo chown root:wheel "$HISTORY_LOG_FILE" 2>/dev/null || true
            else
                print_error "Cannot create log file $HISTORY_LOG_FILE. Please run with sudo or create manually."
                exit 1
            fi
        fi
    fi
    
    # Test if we can write to the log file
    if [[ ! -w "$HISTORY_LOG_FILE" ]]; then
        if command -v sudo >/dev/null 2>&1; then
            # Make the file writable for the current user's group
            sudo chmod g+w "$HISTORY_LOG_FILE" 2>/dev/null || true
        fi
    fi
}

# Enhanced logging function with proper format
write_to_history_log() {
    local level="$1"
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d-%H-%M-%S')
    local log_entry="$timestamp : $CURRENT_USER : $level : $message"
    
    # Write to history log
    if [[ -w "$HISTORY_LOG_FILE" ]]; then
        echo "$log_entry" >> "$HISTORY_LOG_FILE"
    else
        # Try with sudo if direct write fails
        if command -v sudo >/dev/null 2>&1; then
            echo "$log_entry" | sudo tee -a "$HISTORY_LOG_FILE" >/dev/null
        else
            # Fallback to stderr if all else fails
            echo "WARNING: Cannot write to $HISTORY_LOG_FILE: $log_entry" >&2
        fi
    fi
}

# Function to print colored output with logging
print_status() {
    local message="$1"
    echo -e "${BLUE}[INFO]${NC} $message"
    write_to_history_log "INFOS" "$message"
}

print_success() {
    local message="$1"
    echo -e "${GREEN}[SUCCESS]${NC} $message"
    write_to_history_log "INFOS" "$message"
}

print_error() {
    local message="$1"
    echo -e "${RED}[ERROR]${NC} $message" >&2
    write_to_history_log "ERROR" "$message"
}

print_warning() {
    local message="$1"
    echo -e "${YELLOW}[WARNING]${NC} $message"
    write_to_history_log "INFOS" "$message"
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

# Initialize logging system
setup_logging

# Log script initialization
write_to_history_log "INFOS" "InboxGuard script started with user: $CURRENT_USER"
write_to_history_log "INFOS" "Script arguments: $*"

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

# Enhanced log_message function that also writes to history log
log_message() {
    local level="$1"
    shift
    local message="$@"
    local timestamp
    timestamp="$(date +"%Y-%m-%d %H:%M:%S")"
    
    # Write to pipeline log
    echo -e "$timestamp [$level] $message" >> "$PIPELINE_LOG_FILE"
    
    # Also write to history log with proper format
    write_to_history_log "$level" "$message"
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
    python3 start.py
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        write_to_history_log "ERROR" "Fork execution failed with exit code $exit_code"
    fi
    return $exit_code
}

execute_with_threads() {
    print_status "🧵 Executing pipeline using threads..."
    log_message "INFOS" "🧵 Executing pipeline using threads..."
    python3 start.py
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        write_to_history_log "ERROR" "Thread execution failed with exit code $exit_code"
    fi
    return $exit_code
}

execute_with_subshell() {
    print_status "🐚 Executing pipeline in subshell..."
    log_message "INFOS" "🐚 Executing pipeline in subshell..."
    (python3 start.py)
    local exit_code=$?
    if [[ $exit_code -ne 0 ]]; then
        write_to_history_log "ERROR" "Subshell execution failed with exit code $exit_code"
    fi
    return $exit_code
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
    
    # Log completion details only on success
    write_to_history_log "INFOS" "InboxGuard pipeline script completed successfully"
    write_to_history_log "INFOS" "All outputs logged to $HISTORY_LOG_FILE"
else
    print_error "❌ Pipeline failed!"
    log_message "ERROR" "❌ Pipeline failed!"
    write_to_history_log "ERROR" "InboxGuard pipeline script failed with exit code $PIPELINE_EXIT_CODE"
    exit 1
fi