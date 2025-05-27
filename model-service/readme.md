# Phishing Email Detection API

A FastAPI application that detects phishing emails using machine learning.

## Project Structure

```
phishing-detector/
├── main.py              # FastAPI application
├── train_model.py       # Script to train or download the model
├── Dockerfile           # Docker configuration
├── requirements.txt     # Python dependencies
├── models/              # Directory for storing ML models
│   ├── phishing_model.pkl      # Saved model (created during setup)
│   └── tfidf_vectorizer.pkl    # Saved vectorizer (created during setup)
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
