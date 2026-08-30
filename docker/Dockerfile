FROM python:3.11-slim

LABEL maintainer="AVEONE" \
      description="X-ONE: AI Brain for Pentesting"

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    ffmpeg \
    sox \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create non-root user
RUN useradd -m -u 1000 xone && chown -R xone:xone /app
USER xone

# Environment variables
ENV PORT=7777 \
    OLLAMA_URL=http://ollama:11434 \
    OLLAMA_MODEL=dolphin-llama3 \
    MAX_HISTORY=20 \
    MAX_TOKENS=512

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Expose port
EXPOSE ${PORT}

# Start command
CMD ["python3", "-m", "src.server"]
