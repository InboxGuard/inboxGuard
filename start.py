#!/usr/bin/env python3
"""
InboxGuard Pipeline Automation
Runs email extraction, batch processing, and actions automatically.
"""

import os
import sys
import subprocess
import time
import requests
import json
from pathlib import Path

def run_script(script_path, working_dir, timeout=300):
    """Run a Python script in a specific directory with timeout."""
    try:
        print(f"🏃 Running {script_path} in {working_dir}")
        print(f"⏰ Timeout set to {timeout} seconds")
        
        result = subprocess.run([
            sys.executable, script_path
        ], cwd=working_dir, capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            print(f"✅ {script_path} completed successfully")
            if result.stdout:
                print("Output:", result.stdout[-500:])  # Show last 500 chars
            return True
        else:
            print(f"❌ {script_path} failed with return code {result.returncode}")
            if result.stderr:
                print("Error:", result.stderr[-500:])
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {script_path} timed out after {timeout} seconds")
        return False
    except Exception as e:
        print(f"Error running {script_path}: {e}")
        return False

def check_extracted_emails(project_root):
    """Check if emails were extracted successfully."""
    emails_file = project_root / "email-service" / "extracted_emails" / "emails.json"
    if emails_file.exists():
        try:
            with open(emails_file, 'r') as f:
                emails = json.load(f)
            print(f"✅ Found {len(emails)} extracted emails")
            return True, emails
        except:
            return False, None
    return False, None

def check_model_service_running():
    """Check if the model service is running."""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Model service is running")
            return True
    except:
        pass
    return False

def send_emails_to_model_service(emails):
    """Send emails to the model service for processing."""
    try:
        print(f"📤 Sending {len(emails)} emails to model service...")
        
        # Send emails for processing
        response = requests.post(
            "http://localhost:8000/send-latest-batch",
            json={"emails": emails},
            timeout=120
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Model service response received")
            
            # Show summary if available
            if isinstance(result, dict):
                if "summary" in result:
                    summary = result["summary"]
                    print(f"📊 Classification summary:")
                    print(f"   Total: {summary.get('total', 0)}")
                    print(f"   Phishing: {summary.get('phishing', 0)}")
                    print(f"   Legitimate: {summary.get('legitimate', 0)}")
                    print(f"   Suspicious: {summary.get('suspicious', 0)}")
                
                if "results" in result:
                    print(f"📧 Processed {len(result['results'])} emails")
            
            return result
        else:
            print(f"❌ Model service returned error: {response.status_code}")
            print(f"🔍 Error response: {response.text}")
            return None
            
    except requests.exceptions.Timeout:
        print("⏰ Request to model service timed out")
        return None
    except Exception as e:
        print(f"❌ Error communicating with model service: {e}")
        return None

def save_predictions(predictions_response, model_service_dir):
    """Save predictions in the format expected by actions service."""
    try:
        # Create responses directory
        responses_dir = model_service_dir / "responses"
        responses_dir.mkdir(exist_ok=True)
        
        # Generate filename with timestamp
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = responses_dir / f"batch_api_response_{timestamp}.json"
        
        print(f"🔍 Processing model service response...")
        print(f"🔍 Response keys: {list(predictions_response.keys()) if isinstance(predictions_response, dict) else 'Not a dict'}")
        
        # Handle the specific response format from your /send-latest-batch endpoint
        results_list = None
        
        if isinstance(predictions_response, dict):
            # Check for the nested structure from /send-latest-batch
            if "batch_result" in predictions_response:
                batch_result = predictions_response["batch_result"]
                if isinstance(batch_result, dict) and "results" in batch_result:
                    results_list = batch_result["results"]
                    status = batch_result.get("status", "unknown")
                    summary = batch_result.get("summary", {})
                    
                    print(f"✅ Found batch_result with status: {status}")
                    print(f"📊 Summary: {summary}")
                else:
                    print(f"❌ batch_result doesn't contain 'results': {batch_result}")
                    return False
            # Direct format with results
            elif "results" in predictions_response:
                results_list = predictions_response["results"]
                status = predictions_response.get("status", "unknown")
                summary = predictions_response.get("summary", {})
                
                print(f"✅ Found direct results with status: {status}")
                print(f"📊 Summary: {summary}")
            else:
                print(f"❌ No 'batch_result' or 'results' key found. Available keys: {list(predictions_response.keys())}")
                return False
        else:
            print(f"❌ Unexpected response format: {type(predictions_response)}")
            return False
        
        if not results_list:
            print("⚠️ No results found in response")
            return False
        
        print(f"✅ Found {len(results_list)} results to process")
        
        # Convert to simplified format - only UID and prediction
        simplified_results = []
        for result in results_list:
            uid = result.get('uid')
            prediction = result.get('prediction')
            
            if uid is not None and prediction is not None:
                simplified_result = {
                    "custom_id": f"email_{uid}",
                    "response": {
                        "body": {
                            "choices": [
                                {
                                    "message": {
                                        "content": str(prediction)
                                    }
                                }
                            ]
                        }
                    }
                }
                simplified_results.append(simplified_result)
                
                # Map prediction for display
                prediction_label = {
                    1: "phishing",
                    0: "legitimate", 
                    -1: "suspicious"
                }.get(prediction, "unknown")
                
                print(f"  📧 UID {uid}: {prediction_label}")
        
        # Save as JSONL format (one JSON object per line)
        with open(results_file, 'w', encoding='utf-8') as f:
            for result in simplified_results:
                f.write(json.dumps(result) + '\n')
        
        print(f"✅ Predictions saved to: {results_file}")
        print(f"📊 Saved {len(simplified_results)} predictions (UID + prediction only)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving predictions: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_batch_results(model_service_dir):
    """Check if batch results exist."""
    responses_dir = model_service_dir / "responses"
    if responses_dir.exists() and any(responses_dir.glob("batch_api_response_*.json")):
        print("✅ Batch results found!")
        return True
    return False

def main():
    # Get project root directory
    project_root = Path(__file__).parent
    
    print("🚀 Starting InboxGuard Pipeline...")
    
    # Step 1: Extract emails
    print("\n📧 Step 1: Extracting emails...")
    email_service_dir = project_root / "email-service"
    
    email_success = run_script("main.py", email_service_dir, timeout=60)
    
    # Check if we have emails even if the script timed out
    if not email_success:
        print("⚠️ Email extraction timed out, checking for existing data...")
        
    has_emails, emails = check_extracted_emails(project_root)
    if not has_emails:
        print("❌ No emails found. Stopping pipeline.")
        return 1
    
    # Step 2: Check if model service is running and process emails
    print("\n🤖 Step 2: Processing with AI model...")
    model_service_dir = project_root / "model-service"
    
    # Check if model service is running
    if not check_model_service_running():
        print("❌ Model service is not running. Please start the service and try again.")
        return 1
    
    # Send emails to model service for processing
    predictions = send_emails_to_model_service(emails)
    if predictions is None:
        print("❌ Failed to get predictions from model service. Stopping pipeline.")
        return 1
    
    # Save predictions to file
    if not save_predictions(predictions, model_service_dir):
        print("❌ Failed to save predictions. Stopping pipeline.")
        return 1
    
    # Step 3: Verify results were created
    print("\n🔍 Step 3: Verifying AI results...")
    time.sleep(10)  # Wait a moment for files to be written
    if not check_batch_results(model_service_dir):
        print("❌ No results found from AI processing. Stopping pipeline.")
        return 1
    
    # Step 4: Create Gmail labels
    print("\n🏷️ Step 4: Creating Gmail labels...")
    actions_service_dir = project_root / "actions-service"
    if not run_script("labels.py", actions_service_dir, timeout=60):
        print("⚠️ Label creation failed. Continuing with actions processing...")
    
    # Step 5: Process actions
    print("\n⚡ Step 5: Applying email actions...")
    if run_script("main.py", actions_service_dir, timeout=120):
        print("\n🎉 Pipeline completed successfully!")
        return 0
    else:
        print("\n⚠️ Pipeline completed but actions failed.")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n🛑 Pipeline interrupted by user")
        sys.exit(1)