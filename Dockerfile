FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU version first to keep the image lightweight
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files and vector database
COPY app.py llmgeneration.py retrieval.py loader.py ./
COPY data/ ./data/

# Expose FastAPI default port
EXPOSE 8000

# Run uvicorn on port 8000 accessible externally
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
