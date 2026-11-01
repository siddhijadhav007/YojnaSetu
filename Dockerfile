FROM python:3.11-slim

# Prevent python from buffering stdout/stderr and writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=5000
ENV HOST=0.0.0.0

WORKDIR /app

# Install system dependencies needed for compiling psycopg2 and general utils
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY data/ ./data/
COPY ml/ ./ml/
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY wsgi.py .

# Train ML model & ensure database schema initialized
RUN python ml/yojna_setu_ai_ml_model.py && \
    python backend/database.py

EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://localhost:5000/api/health || exit 1

# Start production server
CMD ["python", "wsgi.py"]
