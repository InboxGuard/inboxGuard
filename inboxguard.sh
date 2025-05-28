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
    echo "  -h, --help               Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -e user@gmail.com -p \"your app password\""
    echo "  $0 --email user@gmail.com --password \"your app password\" --num-emails 20"
    echo ""
    echo "Note: Use Gmail App Password, not your regular password"
    echo "      If password contains spaces, wrap it in quotes"
}

# Default values
NUM_EMAILS=10
EMAIL=""
PASSWORD=""

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

if python3 start.py; then
    print_success "🎉 InboxGuard pipeline completed successfully!"
    print_status "Check the logs in each service directory for detailed information."
else
    print_error "❌ Pipeline failed!"
    exit 1
fi