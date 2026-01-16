# Dockerfile for K8s Challenge App
# This is pre-built for you - focus on the Kubernetes manifests!

FROM python:3.11-slim

WORKDIR /app

# Install Flask
RUN pip install --no-cache-dir flask==3.0.0

# Copy application
COPY app.py .

# Create non-root user
RUN useradd --create-home appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

# Run the app
CMD ["python", "app.py"]
