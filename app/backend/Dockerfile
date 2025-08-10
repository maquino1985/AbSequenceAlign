# Backend Dockerfile - Uses base image with dependencies pre-installed
FROM absequencealign-backend-base:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CONDA_AUTO_UPDATE_CONDA=false \
    PATH=/opt/conda/bin:$PATH

# Set working directory
WORKDIR /app

# Copy backend source code
COPY app/backend ./

# Copy data directory from project root
COPY data ./data

# Install additional Python dependencies if needed
RUN conda run -n AbSequenceAlign pip install --no-cache-dir uvicorn[standard] gunicorn

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser
RUN chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD conda run -n AbSequenceAlign python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Start the application
CMD ["conda", "run", "-n", "AbSequenceAlign", "gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--timeout", "120"]
