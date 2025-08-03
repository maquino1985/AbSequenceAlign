.PHONY: help setup dev test docker-build docker-run docker-stop clean

help: ## Show this help message
	@echo "AbSequenceAlign Development Commands"
	@echo "=================================="
	@echo ""
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup: ## Set up development environment
	@echo "Setting up development environment..."
	@./scripts/setup.sh

conda-setup: ## Set up conda environment
	@echo "Setting up conda environment..."
	@conda env create -f environment.yml

conda-activate: ## Activate conda environment
	@echo "Activating conda environment..."
	@conda activate absequencealign

dev: ## Start development server
	@echo "Starting development server..."
	@./scripts/dev.sh

test: ## Run tests
	@echo "Running tests..."
	@./scripts/test.sh

docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker-compose build

docker-run: ## Run with Docker
	@echo "Starting with Docker..."
	docker-compose up

docker-stop: ## Stop Docker containers
	@echo "Stopping Docker containers..."
	docker-compose down

docker-logs: ## Show Docker logs
	@echo "Showing Docker logs..."
	docker-compose logs -f

docker-test: ## Run comprehensive Docker tests
	@echo "Running comprehensive Docker tests..."
	@./scripts/test_docker.sh

docker-test-internal: ## Run internal Docker tests
	@echo "Running internal Docker tests..."
	@docker-compose up -d
	@sleep 10
	@docker-compose exec -T absequencealign python test_docker_internal.py
	@docker-compose down

clean: ## Clean up development files
	@echo "Cleaning up..."
	rm -rf __pycache__
	rm -rf app/__pycache__
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

install-deps: ## Install system dependencies (Ubuntu/Debian)
	@echo "Installing system dependencies..."
	sudo apt-get update
	sudo apt-get install -y python3-venv python3-pip
	sudo apt-get install -y muscle mafft clustalo curl

install-deps-mac: ## Install system dependencies (macOS)
	@echo "Installing system dependencies..."
	brew install muscle mafft clustalo curl

format: ## Format code with black
	@echo "Formatting code..."
	python -m black app/ test_*.py

lint: ## Lint code with flake8
	@echo "Linting code..."
	python -m flake8 app/ test_*.py

type-check: ## Type check with mypy
	@echo "Type checking..."
	python -m mypy app/

check: format lint type-check ## Run all code quality checks 