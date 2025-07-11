#!/usr/bin/env python3
"""
Gmail Email Processor Script

This script connects to Gmail via IMAP, reads predictions from the latest
batch API response file, and performs actions on emails based on those predictions.
"""

import imaplib
import email
import json
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv
import os
from pathlib import Path
from email.message import EmailMessage
import glob
from datetime import datetime

# Configure logging to both file and console
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# File handler
log_filename = log_dir / f"gmail_processor_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
file_handler = logging.FileHandler(log_filename)
file_handler.setFormatter(formatter)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


class GmailProcessor:
    """Gmail email processor that handles IMAP connections and email actions."""
    
    def __init__(self):
        """Initialize the Gmail processor with environment variables."""
        load_dotenv()
        self.gmail_address = os.getenv('GMAIL_ADDRESS')
        self.gmail_password = os.getenv('GMAIL_PASSWORD')
        self.mail = None
        self.predictions_data = self.load_latest_predictions()
        
        if not self.gmail_address or not self.gmail_password:
            raise ValueError("GMAIL_ADDRESS and GMAIL_PASSWORD must be set in .env file")
    
    def load_latest_predictions(self) -> Dict:
        """
        Load predictions from the latest batch API response file.
        
        Returns:
            Dict: Predictions data with email UIDs as keys
        """
        responses_dir = Path("/Users/admin/Projects/enset/InboxGuard/model-service/responses")
        
        try:
            # Find all batch_api_response_*.json files
            pattern = str(responses_dir / "batch_api_response_*.json")
            json_files = glob.glob(pattern)
            
            if not json_files:
                logger.warning(f"No batch API response files found in {responses_dir}")
                return {}
            
            # Get the latest file (most recent modification time)
            latest_file = max(json_files, key=os.path.getmtime)
            logger.info(f"Loading predictions from latest file: {latest_file}")
            
            predictions = {}
            
            # Read file line by line since it's JSONL format
            with open(latest_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:
                        continue
                    
                    try:
                        data = json.loads(line)
                        logger.info(f"Line {line_num}: {data}")
                        
                        # Extract custom_id and prediction
                        if 'custom_id' in data and 'response' in data:
                            custom_id = data['custom_id']
                            response = data['response']
                            
                            # Extract UID from custom_id (remove "email_" prefix)
                            if custom_id.startswith('email_'):
                                uid = custom_id[6:]  # Remove "email_" prefix
                            else:
                                uid = custom_id
                            
                            # Extract prediction from response
                            if 'body' in response and 'choices' in response['body']:
                                choices = response['body']['choices']
                                if choices and len(choices) > 0:
                                    content = choices[0].get('message', {}).get('content', '')
                                    
                                    try:
                                        # Convert string prediction to integer
                                        prediction_value = int(content.strip().strip('"'))
                                        
                                        # Create prediction data structure
                                        prediction_data = {
                                            'prediction': prediction_value,
                                            'confidence': 1.0,  # Default confidence
                                            'message': f'Prediction from OpenAI: {prediction_value}'
                                        }
                                        
                                        predictions[uid] = prediction_data
                                        logger.info(f"Processed UID {uid} with prediction {prediction_value}")
                                        
                                    except (ValueError, TypeError) as e:
                                        logger.error(f"Failed to parse prediction value '{content}' for UID {uid}: {e}")
                        
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse JSON on line {line_num}: {e}")
                        continue
            
            logger.info(f"Successfully loaded {len(predictions)} email predictions")
            logger.info(f"Prediction UIDs: {list(predictions.keys())}")
            
            return predictions
            
        except Exception as e:
            logger.error(f"Error loading predictions from {responses_dir}: {e}")
            return {}
    
    def connect(self) -> bool:
        """
        Connect to Gmail via IMAP SSL.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Connect to Gmail IMAP server
            self.mail = imaplib.IMAP4_SSL('imap.gmail.com')
            self.mail.login(self.gmail_address, self.gmail_password)
            logger.info(f"Successfully connected to Gmail for {self.gmail_address}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Gmail: {e}")
            return False
    
    def disconnect(self):
        """Close the IMAP connection."""
        if self.mail:
            try:
                # Check if we have a mailbox selected
                try:
                    self.mail.close()
                except:
                    pass  # Ignore errors if no mailbox was selected
                self.mail.logout()
                logger.info("Disconnected from Gmail")
            except Exception as e:
                logger.warning(f"Error during disconnect: {e}")
    
    def fetch_email_by_uid(self, email_uid: str, label: str = 'INBOX') -> Optional[EmailMessage]:
        """
        Fetch a specific email by UID from specified label/folder.
        
        Args:
            email_uid (str): Email UID to fetch
            label (str): Gmail label/folder to search (default: 'INBOX')
            
        Returns:
            Optional[EmailMessage]: Email message object or None if not found
        """
        try:
            # Select the mailbox
            self.mail.select(label)
            
            # Fetch specific email by UID
            status, msg_data = self.mail.uid('fetch', email_uid, '(RFC822)')
            
            if status != 'OK':
                logger.error(f"Failed to fetch email UID {email_uid}: {status}")
                return None
            
            if not msg_data or not msg_data[0]:
                logger.warning(f"Email UID {email_uid} not found in {label}")
                return None
            
            # Parse email message
            email_message = email.message_from_bytes(msg_data[0][1])
            logger.info(f"Successfully fetched email UID {email_uid}")
            return email_message
            
        except Exception as e:
            logger.error(f"Error fetching email UID {email_uid}: {e}")
            return None
    
    def perform_action(self, email_uid: str, prediction: int) -> bool:
        """
        Perform action on email based on prediction.
        
        Args:
            email_uid (str): Email UID
            prediction (int): Action to perform (1=delete, 0=ignore, -1=move to suspicious)
            
        Returns:
            bool: True if action successful, False otherwise
        """
        print(f"Performing action on email UID: {email_uid}")
        logger.info(f"Performing action on email UID: {email_uid} with prediction: {prediction}")
        
        try:
            # Select INBOX to ensure we're working with the right mailbox
            self.mail.select('INBOX')
            
            if prediction == 1:
                # Delete email (move to Trash) - assuming this means phishing
                self.mail.uid('store', email_uid, '+X-GM-LABELS', 'inboxguard-phishing')
                # Remove from inbox
                self.mail.uid('store', email_uid, '-X-GM-LABELS', '\\Inbox')
                logger.info(f"Moved email UID {email_uid} to inboxguard-phishing label")
                
            elif prediction == -1:
                # Move email to "suspicious" sublabel
                self.mail.uid('store', email_uid, '+X-GM-LABELS', 'inboxguard-suspicious')
                # Remove from inbox
                self.mail.uid('store', email_uid, '-X-GM-LABELS', '\\Inbox')
                logger.info(f"Moved email UID {email_uid} to inboxguard-suspicious label")
                
            elif prediction == 0:
                # Move to safe sublabel (or do nothing - your choice)
                self.mail.uid('store', email_uid, '+X-GM-LABELS', 'inboxguard-safe')
                # Remove from inbox
                self.mail.uid('store', email_uid, '-X-GM-LABELS', '\\Inbox')
                logger.info(f"Moved email UID {email_uid} to inboxguard-safe label")
            else:
                logger.warning(f"Unknown prediction value {prediction} for email UID {email_uid}")
                return False
                
            return True
            
        except Exception as e:
            logger.error(f"Error performing action on email UID {email_uid}: {e}")
            return False
    
    def process_email_by_uid(self, email_uid: str, prediction_data: Dict, label: str = 'INBOX') -> bool:
        """
        Process a specific email by UID using provided prediction data.
        
        Args:
            email_uid (str): Email UID to process
            prediction_data (Dict): Prediction data for this email
            label (str): Gmail label/folder where email is located (default: 'INBOX')
            
        Returns:
            bool: True if processing successful, False otherwise
        """
        logger.info(f"Processing email UID: {email_uid}")
        logger.info(f"Prediction data type: {type(prediction_data)}")
        logger.info(f"Prediction data: {prediction_data}")
        
        try:
            # Ensure prediction_data is a dictionary
            if not isinstance(prediction_data, dict):
                logger.error(f"Prediction data for UID {email_uid} is not a dictionary: {type(prediction_data)}")
                return False
            
            # Extract prediction value
            prediction = prediction_data.get('prediction')
            confidence = prediction_data.get('confidence', 0.0)
            message = prediction_data.get('message', 'No message')
            
            if prediction is None:
                logger.warning(f"No prediction found for email UID {email_uid}")
                logger.warning(f"Available keys in prediction data: {list(prediction_data.keys())}")
                return False
            
            # Log prediction details
            logger.info(f"Email UID {email_uid}: Prediction={prediction}, "
                       f"Confidence={confidence:.3f}, Message='{message}'")
            
            # Perform action based on prediction
            success = self.perform_action(email_uid, prediction)
            
            if success:
                logger.info(f"Successfully processed email UID {email_uid}")
            else:
                logger.error(f"Failed to process email UID {email_uid}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error processing email UID {email_uid}: {e}")
            return False
    
    def process_all_predictions(self) -> Dict[str, bool]:
        """
        Process all emails based on loaded predictions.
        
        Returns:
            Dict[str, bool]: Results for each email UID (True=success, False=failure)
        """
        if not self.predictions_data:
            logger.error("No predictions data loaded. Cannot process emails.")
            return {}
        
        results = {}
        total_emails = len(self.predictions_data)
        logger.info(f"Starting to process {total_emails} emails...")
        
        for email_uid, prediction_data in self.predictions_data.items():
            try:
                success = self.process_email_by_uid(email_uid, prediction_data)
                results[email_uid] = success
                
                # Small delay to avoid overwhelming the server
                import time
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to process email UID {email_uid}: {e}")
                results[email_uid] = False
        
        # Summary
        successful = sum(1 for success in results.values() if success)
        failed = total_emails - successful
        
        logger.info(f"Processing complete: {successful} successful, {failed} failed out of {total_emails} total")
        
        return results


def main():
    """Main function to run the Gmail processor."""
    processor = None
    
    try:
        logger.info("Starting Gmail Email Processor")
        logger.info(f"Log file: {log_filename}")
        
        # Initialize processor
        processor = GmailProcessor()
        
        # Check if predictions were loaded
        if not processor.predictions_data:
            logger.error("No predictions data available. Exiting.")
            return
        
        # Connect to Gmail
        if not processor.connect():
            logger.error("Failed to connect to Gmail. Exiting.")
            return
        
        # Process all emails based on predictions
        results = processor.process_all_predictions()
        
        # Print summary
        print(f"\nProcessing Summary:")
        print(f"Total emails: {len(results)}")
        print(f"Successful: {sum(1 for success in results.values() if success)}")
        print(f"Failed: {sum(1 for success in results.values() if not success)}")
        print(f"Log file saved to: {log_filename}")
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        
    finally:
        # Always disconnect
        if processor:
            processor.disconnect()


if __name__ == "__main__":
    main()