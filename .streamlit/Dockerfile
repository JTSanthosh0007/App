# Use Python 3.9 slim image
FROM python:3.9-slim

# Set working directory
WORKDIR /demo

# Install system dependencies with minimal layers
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    software-properties-common \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy requirements first
COPY requirements.txt .

# Install Python dependencies with caching disabled
RUN pip install --no-cache-dir -r requirements.txt

# Create necessary directories
RUN mkdir -p platforms
RUN mkdir -p .streamlit

# Copy platform files
COPY platforms/__init__.py platforms/
COPY platforms/router.py platforms/
COPY platforms/phonepe.py platforms/
COPY platforms/paytm.py platforms/

# Copy other necessary files
COPY app.py .
COPY utils.py .
COPY statement_parser.py .
COPY supabase_config.py .
COPY firebase_config.py .
COPY platform_pages.py .
COPY payment.py .
COPY .streamlit/config.toml .streamlit/
COPY firebase-service-account.json .

# Set environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
ENV STREAMLIT_SERVER_ENABLECACHING=true
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
ENV STREAMLIT_CACHE_PERSIST=true

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Command to run the application
CMD ["streamlit", "run", "app.py"]
