#  Base image 
FROM python:3.11-slim

#  System deps 
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

#  Working directory 
WORKDIR /app

#  Install Python dependencies 
# Copy requirements first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#  Copy project files 
COPY . .

#  HuggingFace Spaces runs as non-root user 
RUN useradd -m -u 1000 hfuser && chown -R hfuser:hfuser /app
USER hfuser

#  Expose port (HuggingFace Spaces default) 
EXPOSE 7860

#  Health check 
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:7860/health || exit 1

#  Run 
CMD ["python", "app.py"]
