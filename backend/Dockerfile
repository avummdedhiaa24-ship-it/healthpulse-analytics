# ── Stage: runtime ────────────────────────────────────────────────────────
FROM python:3.11-slim
 
# Set working directory
WORKDIR /app
 
# Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
 
# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*
 
# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# Copy application code
COPY app/ ./app/
 
# Copy environment file (will be overridden by docker-compose env_file)
COPY .env .
 
# Expose port
EXPOSE 8000
 
# Run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
 