FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
# ffmpeg will be needed later for video processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create workspace directories
RUN mkdir -p workspace/input workspace/slides workspace/videos

# Expose port (Render uses PORT env variable)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Run the application
# Render provides PORT env variable, default to 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
