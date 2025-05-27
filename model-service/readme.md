# Model Service - Phishing Email Detection API

The Model Service is a FastAPI-based microservice that provides machine learning capabilities for detecting phishing emails in the InboxGuard system.

## 🎯 Overview

This service implements a trained machine learning model that analyzes email content (subject and body) to classify emails as:

- **Legitimate** (0): Safe emails
- **Phishing** (1): Malicious emails attempting to steal information
- **Suspicious** (-1): Uncertain classification (low confidence)

## 🏗️ Architecture

The service uses:

- **FastAPI** for the REST API framework
- **Scikit-learn** for machine learning models
- **TF-IDF Vectorization** for text feature extraction
- **Joblib** for model persistence

## 📁 Project Structure

```
model-service/
├── main.py                    # FastAPI application and endpoints
├── requirements.txt           # Python dependencies
├── README.md                 # This file
├── sample_email.json         # Sample phishing email data
├── sample_ai.json           # Sample email data for testing
└── ai/
    └── train_model/
        ├── emails_dataset.csv      # Training dataset
        ├── generate_dataset.ipynb  # Dataset generation notebook
        ├── train_model.ipynb      # Model training notebook
        └── models/
            ├── phishing_model.pkl      # Trained ML model
            └── tfidf_vectorizer.pkl    # TF-IDF vectorizer
```

## Setup Instructions

### Option 1: Using Docker (Recommended)

1. Make sure Docker is installed on your system
2. Clone/download this repository
3. Navigate to the project directory
4. Build the Docker image:

```bash
docker build -t phishing-detector .
```

5. Run the Docker container:

```bash
docker run -p 8000:8000 phishing-detector
```

The API will be available at http://localhost:8000

### Option 2: Manual Setup

1. Clone/download this repository
2. Navigate to the project directory
3. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install the requirements:

```bash
pip install -r requirements.txt
```

5. Train or download the model:

```bash
python train_model.py
```

6. Start the FastAPI application:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

## API Usage

### Detect Phishing Email

**Endpoint:** `POST /detect-phishing`

**Request:**

- Send a JSON file containing the email content as a form file upload

```bash
docker build -t phishing-detector .
```

docker run -p 8000:8000 phishing-detector

````

```bash
curl -X POST "http://localhost:8000/detect-phishing" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@email.json"
````

**Example JSON file (email.json):**

```json
{
  "subject": "Urgent: Your account has been suspended",
  "body": "Dear user, your account has been suspended. Click here to verify your account: http://suspicious-link.com",
  "sender": "security@suspicious-domain.com"
}
```

**Response:**

```json
{
  "status": "success",
  "prediction": 1,
  "confidence": 0.92,
  "message": "Phishing email detected"
}
```

### Response Values:

- `prediction`:

  - `1`: Phishing email
  - `0`: Legitimate email
  - `-1`: Suspicious/uncertain

- `confidence`: Probability score between 0 and 1

## Health Check

**Endpoint:** `GET /health`

**Example:**

```bash
curl -X GET "http://localhost:8000/health"
```

**Response:**

```json
{
  "status": "healthy"
}
```

## Model Training Details

The model provided is a simple RandomForest classifier trained on TF-IDF features extracted from email text. For a production system, consider:

1. Using a larger, more diverse dataset
2. Implementing more sophisticated features (URLs analysis, header analysis, etc.)
3. Using more advanced models (like deep learning approaches)
4. Regularly retraining the model with new data

## Swagger Documentation

FastAPI provides automatic Swagger documentation at:

- http://localhost:8000/docs
