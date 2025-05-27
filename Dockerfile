FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY model-service/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Create models directory (models already exist)
RUN mkdir -p ai/train_model/models

# Expose the port that FastAPI will run on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "model-service.main:app", "--host", "0.0.0.0", "--port", "8000"]
