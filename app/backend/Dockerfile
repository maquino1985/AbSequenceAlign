# Backend Dockerfile - Python FastAPI with microconda
FROM continuumio/miniconda3:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    CONDA_AUTO_UPDATE_CONDA=false \
    PATH=/opt/conda/bin:$PATH

# Set working directory
WORKDIR /app

# Update system packages
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy environment file
COPY environment.yml .

# Create conda environment
RUN conda env create -f environment.yml && \
    conda clean -afy

# Activate environment
SHELL ["conda", "run", "-n", "AbSequenceAlign", "/bin/bash", "-c"]

# Copy source code
COPY . .

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
