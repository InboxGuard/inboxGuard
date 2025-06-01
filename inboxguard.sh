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
    echo "Options:"
    echo "  -e, --email EMAIL        Gmail address"
    echo "  -p, --password PASSWORD  Gmail app password (use quotes if it contains spaces)"
    echo "  -n, --num-emails NUM     Number of emails to process (default: 10)"
    echo "  -f, --fork               Execute tasks using fork (child processes)"
    echo "  -t, --thread             Execute tasks using threads"
    echo "  -s, --subshell           Execute tasks in a subshell"
    echo "  -l, --log DIR            Specify a directory for logging"
    echo "  -r, --restore            Reset parameters to default (requires admin privileges)"
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -e user@gmail.com -p \"your app password\""
    echo "  $0 --email user@gmail.com --password \"your app password\" --num-emails 20"
    echo "  $0 --fork"
    echo "  $0 --log /path/to/logs"
    echo ""
    echo "Note: Use Gmail App Password, not your regular password"
    echo "      If password contains spaces, wrap it in quotes"
}

# Default values
NUM_EMAILS=10
EMAIL=""
PASSWORD=""
LOG_DIR="/var/log/inboxguard"
RESTORE=false
EXEC_MODE="default"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
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
        -f|--fork)
            EXEC_MODE="fork"
            shift
            ;;
        -t|--thread)
            EXEC_MODE="thread"
            shift
            ;;
        -s|--subshell)
            EXEC_MODE="subshell"
            shift
            ;;
        -l|--log)
            LOG_DIR="$2"
            shift 2
            ;;
        -r|--restore)
            RESTORE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Validate required arguments
if [[ -z "$EMAIL" || -z "$PASSWORD" ]]; then
    print_error "Email and password are required!"
    show_usage
    exit 1
fi

# Handle restore option
if [[ "$RESTORE" == true ]]; then
    if [[ $(id -u) -ne 0 ]]; then
        print_error "Restore option requires admin privileges!"
        exit 1
    fi
    print_status "Restoring default parameters..."
    # Add restore logic here
    exit 0
fi

# Handle logging directory
if [[ ! -d "$LOG_DIR" ]]; then
    mkdir -p "$LOG_DIR"
fi
LOG_FILE="$LOG_DIR/history.log"

# Add logging function
log_message() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d-%H-%M-%S')
    local username=$(whoami)
    echo "$timestamp : $username : $level : $message" | tee -a "$LOG_FILE"
}

log_message "INFOS" "Starting script with execution mode: $EXEC_MODE"

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="$SCRIPT_DIR/.env"

print_status "🚀 Starting InboxGuard Pipeline..."
print_status "Email: $EMAIL"
print_status "Number of emails: $NUM_EMAILS"

# Create or update .env file
print_status "📝 Creating environment file..."
cat > "$ENV_FILE" << EOF
GMAIL_ADDRESS=$EMAIL
GMAIL_PASSWORD=$PASSWORD
NUM_EMAILS=$NUM_EMAILS
EOF

print_success "Environment file created at $ENV_FILE"

# Run the Python pipeline
print_status "🐍 Starting Python pipeline..."
cd "$SCRIPT_DIR"

# Check if the model service is running
MODEL_SERVICE_PORT=8000
if ! lsof -i :$MODEL_SERVICE_PORT > /dev/null; then
    print_status "🤖 Model service is not running. Starting it now..."
    (cd "$SCRIPT_DIR/model-service" && python3 main.py &) > /dev/null 2>&1
    sleep 5  # Wait for the service to start

    # Verify if the service started successfully
    if ! lsof -i :$MODEL_SERVICE_PORT > /dev/null; then
        print_error "Failed to start the model service. Please check the logs."
        exit 1
    fi
    print_success "Model service started successfully."
else
    print_status "🤖 Model service is already running."
fi

if python3 start.py; then
    print_success "🎉 InboxGuard pipeline completed successfully!"
    print_status "Check the logs in each service directory for detailed information."
else
    print_error "❌ Pipeline failed!"
    exit 1
fi