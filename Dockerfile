# Use Miniforge base image for optimized conda-forge and bioconda usage
FROM condaforge/miniforge3:latest

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Set work directory
WORKDIR /app

# Channels are already configured with miniforge but can be explicitly added and set to strict priority again for clarity (redundant but harmless)
RUN conda config --add channels bioconda && \
    conda update -n base -c defaults conda

# Install bioinformatics tools and Python dependencies via conda
RUN conda install -y \
    python=3.11 \ 
    muscle \
    mafft \
    hmmer \
    anarci \
    clustalo \
    biopython==1.84 \
    scipy \
    pandas \
    fastapi \
    uvicorn \
    pydantic \
    python-multipart \
    python-jose \
    passlib \
    python-dotenv \
    httpx \
    pytest \
    pytest-asyncio \
    pytest-cov \
    black \
    flake8 \
    mypy \
    isort \
    git \
    curl \
    && conda clean -afy

# Install clustalo via apt (not available in conda)
# RUN apt-get update && apt-get install -y clustalo && rm -rf /var/lib/apt/lists/*

# Install ANARCI via pip (conda doesn't have it)
# RUN pip install --no-cache-dir git+https://github.com/oxpig/ANARCI.git

# Verify tools are installed and working
RUN muscle -version && \
    mafft --version && \
    clustalo --version && \
    hmmsearch -h

# Copy application code
COPY . .

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
