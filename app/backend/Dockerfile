# Backend Dockerfile - Uses base image with dependencies pre-installed
# In CI, this will be pulled from registry; locally, it will use the local image
ARG BASE_IMAGE=ghcr.io/maquino1985/absequencealign-backend-base:latest
FROM ${BASE_IMAGE}

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CONDA_AUTO_UPDATE_CONDA=false \
    PATH=/opt/conda/bin:$PATH

ENV CONDA_ENV=AbSequenceAlign
# Set working directory
WORKDIR /app

# Copy backend source code with proper package structure
COPY app/backend ./backend

# Copy data directory from project root
COPY data/ ./data/

# Install additional Python dependencies if needed
RUN conda run -n ${CONDA_ENV} pip install --no-cache-dir "uvicorn[standard]" gunicorn

# Create a writable directory for pytest cache
RUN mkdir -p /tmp/pytest_cache && chmod 777 /tmp/pytest_cache

# Switch to appuser (user already exists in base image)
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD conda run -n AbSequenceAlign python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Start the application
CMD ["conda", "run", "-n", "AbSequenceAlign", "gunicorn", "backend.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000", "--timeout", "120"]
