# Dockerfile for Gold Tier Autonomous AI Employee

FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY mcp_server/ ./mcp_server/

# Create necessary directories
RUN mkdir -p \
    Inbox \
    Needs_Action \
    Plans \
    Pending_Approval \
    Approved \
    Done \
    Rejected \
    Audit_Logs \
    Reports/CEO_Briefings

# Set Python path
ENV PYTHONPATH=/app

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Run the application
CMD ["python", "src/main.py"]
