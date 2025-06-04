# Build stage for Node.js
FROM node:18-alpine AS node-builder
WORKDIR /app
COPY backend/package*.json ./
RUN npm ci --only=production
COPY backend/ .

# Build stage for Python
FROM python:3.9-slim AS python-builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Final stage
FROM python:3.9-slim
WORKDIR /app

# Copy only necessary files from previous stages
COPY --from=node-builder /app /app/backend
COPY --from=python-builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY scripts/ /app/scripts/
COPY .env /app/

# Clean up
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV NODE_ENV=production

# Expose ports
EXPOSE 10000

# Start the application
CMD ["sh", "-c", "cd backend && npm start & python /app/scripts/statement_parser.py"] 