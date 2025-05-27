from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Optional, Union
import json
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import os

app = FastAPI(title="Phishing Email Detector API")

# Path where the model and vectorizer will be stored
MODEL_PATH = "ai/train_model/models/phishing_model.pkl"
VECTORIZER_PATH = "ai/train_model/models/tfidf_vectorizer.pkl"

# Load the model and vectorizer
@app.on_event("startup")
async def load_model():
    try:
        global model, vectorizer
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VECTORIZER_PATH)
        print("Model and vectorizer loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
        print("Please ensure model files exist by running the training script first")


class EmailInput(BaseModel):
    id: str
    sender: str
    subject: str
    body: str


class PredictionResult(BaseModel):
    id: str
    prediction: int
    confidence: float
    message: str
    input_source: Optional[Dict] = None


class SinglePredictionResponse(BaseModel):
    status: str
    result: PredictionResult


class BatchPredictionResponse(BaseModel):
    status: str
    results: List[PredictionResult]
    summary: Dict[str, int]


def extract_email_text(email_data: Dict) -> str:
    """Extract email text content from subject and body only"""
    subject = email_data.get("subject", "")
    body = email_data.get("body", "")
    return f"{subject} {body}".strip()


def analyze_email(email_data: Dict, email_id: Optional[str] = None) -> PredictionResult:
    """Analyze a single email and return prediction results"""
    # Check if model and vectorizer are loaded
    if 'model' not in globals() or 'vectorizer' not in globals():
        raise HTTPException(status_code=500, detail="Model or vectorizer not loaded")
    
    email_text = extract_email_text(email_data)
    if not email_text:
        return PredictionResult(
            id=email_id or email_data.get("id", ""),
            prediction=0,  # Suspicious now returns 0
            confidence=0.0,
            message="Empty email content",
            input_source={"subject": email_data.get("subject", ""), "sender": email_data.get("sender", "")}
        )
    features = vectorizer.transform([email_text])
    prediction = model.predict(features)[0]
    probabilities = model.predict_proba(features)[0]
    max_prob = max(probabilities)
    confidence = float(max_prob)
    if confidence < 0.7:
        final_prediction = -1  # Suspicious now returns -1
        message = "Suspicious email - uncertain classification"
    else:
        final_prediction = int(prediction)
        message = "Phishing email detected" if prediction == 1 else "Legitimate email"
    input_source = {
        "subject": email_data.get("subject", ""),
        "sender": email_data.get("sender", "")
    }
    return PredictionResult(
        id=email_id or email_data.get("id", ""),
        prediction=final_prediction,
        confidence=confidence,
        message=message,
        input_source=input_source
    )


@app.post("/detect-phishing-upload-file", response_model=Union[SinglePredictionResponse, BatchPredictionResponse])
async def detect_phishing_upload_file(file: UploadFile = File(...)):
    """
    Detect phishing emails from uploaded JSON file (single email or multiple emails)

    The JSON can be:
    1. A single email object
    2. An array of email objects
    3. A nested structure with emails under properties
    
    Returns:
    - prediction: 1 (Phishing), 0 (Not Phishing), -1 (Suspicious/Uncertain)
    """
    try:
        # Read and parse the uploaded JSON file
        content = await file.read()
        data = json.loads(content)
        
        # Check if we have a single email or multiple emails
        if isinstance(data, list):
            # Process list of emails
            results = [analyze_email(email) for email in data]
            
            # Generate summary statistics
            summary = {
                "total": len(results),
                "phishing": sum(1 for r in results if r.prediction == 1),
                "legitimate": sum(1 for r in results if r.prediction == 0),
                "suspicious": sum(1 for r in results if r.prediction == -1)
            }
            
            return BatchPredictionResponse(
                status="success",
                results=results,
                summary=summary
            )
            
        elif isinstance(data, dict):
            # Check if this is a single email or a container with multiple emails
            if "emails" in data and isinstance(data["emails"], list):
                # Container with list of emails
                results = [analyze_email(email) for email in data["emails"]]
                
                # Generate summary statistics
                summary = {
                    "total": len(results),
                    "phishing": sum(1 for r in results if r.prediction == 1),
                    "legitimate": sum(1 for r in results if r.prediction == 0),
                    "suspicious": sum(1 for r in results if r.prediction == -1)
                }
                
                return BatchPredictionResponse(
                    status="success",
                    results=results,
                    summary=summary
                )
                
            else:
                # Single email object
                result = analyze_email(data)
                return SinglePredictionResponse(
                    status="success",
                    result=result
                )
                
        else:
            raise HTTPException(
                status_code=400, 
                detail="Invalid JSON format. Expected a single object or an array of objects."
            )
            
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


@app.post("/detect-phishing-batch", response_model=BatchPredictionResponse)
async def detect_phishing_batch(emails: List[EmailInput]):
    """
    Batch endpoint for analyzing multiple emails at once via JSON body
    """
    try:
        # Process each email - use the email's own ID instead of generating one
        results = [analyze_email(email.dict()) for email in emails]
        
        # Generate summary statistics
        summary = {
            "total": len(results),
            "phishing": sum(1 for r in results if r.prediction == 1),
            "legitimate": sum(1 for r in results if r.prediction == 0),
            "suspicious": sum(1 for r in results if r.prediction == -1)
        }
        
        return BatchPredictionResponse(
            status="success",
            results=results,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch prediction error: {str(e)}")


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)