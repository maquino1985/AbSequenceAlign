# AbSequenceAlign Development Makefile

# Variables
COMPOSE_FILE = docker-compose.yml
COMPOSE_PROD_FILE = docker-compose.prod.yml
BACKEND_DIR = app/backend
FRONTEND_DIR = app/frontend

# Colors for output
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help build up down logs test clean install dev prod

# Default target
help: ## Show this help message
	@echo "$(GREEN)AbSequenceAlign Development Commands$(NC)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

# Development commands
install: ## Install all dependencies
	@echo "$(GREEN)Installing backend dependencies...$(NC)"
	cd $(BACKEND_DIR) && conda env create -f environment.yml || conda env update -f environment.yml
	@echo "$(GREEN)Installing frontend dependencies...$(NC)"
	cd $(FRONTEND_DIR) && npm install

dev-backend: ## Start backend in development mode
	@echo "$(GREEN)Starting backend in development mode...$(NC)"
	cd $(BACKEND_DIR) && conda run -n AbSequenceAlign python main.py

dev-frontend: ## Start frontend in development mode
	@echo "$(GREEN)Starting frontend in development mode...$(NC)"
	cd $(FRONTEND_DIR) && npm run dev

dev: ## Start both frontend and backend in development mode
	@echo "$(GREEN)Starting development environment...$(NC)"
	@make -j2 dev-backend dev-frontend

# Testing commands
test: ## Run all tests
	@echo "$(GREEN)Running backend tests...$(NC)"
	cd $(BACKEND_DIR) && conda run -n AbSequenceAlign python -m pytest tests/ -v
	@echo "$(GREEN)Running frontend tests...$(NC)"
	cd $(FRONTEND_DIR) && npm run test

test-backend: ## Run backend tests only
	@echo "$(GREEN)Running backend tests...$(NC)"
	cd $(BACKEND_DIR) && conda run -n AbSequenceAlign python -m pytest tests/ -v

test-frontend: ## Run frontend tests only
	@echo "$(GREEN)Running frontend tests...$(NC)"
	cd $(FRONTEND_DIR) && npm run test

lint: ## Run linting for both frontend and backend
	@echo "$(GREEN)Running backend linting...$(NC)"
	cd $(BACKEND_DIR) && conda run -n AbSequenceAlign black . && conda run -n AbSequenceAlign flake8 . && conda run -n AbSequenceAlign mypy .
	@echo "$(GREEN)Running frontend linting...$(NC)"
	cd $(FRONTEND_DIR) && npm run lint

# Docker commands
build: ## Build Docker images
	@echo "$(GREEN)Building Docker images...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build

up: ## Start application with Docker
	@echo "$(GREEN)Starting application...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d

down: ## Stop application
	@echo "$(GREEN)Stopping application...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down

logs: ## View application logs
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-backend: ## View backend logs
	docker-compose -f $(COMPOSE_FILE) logs -f backend

logs-frontend: ## View frontend logs
	docker-compose -f $(COMPOSE_FILE) logs -f frontend

# Production commands
prod-build: ## Build production Docker images
	@echo "$(GREEN)Building production Docker images...$(NC)"
	docker-compose -f $(COMPOSE_PROD_FILE) build

prod-up: ## Start production application
	@echo "$(GREEN)Starting production application...$(NC)"
	docker-compose -f $(COMPOSE_PROD_FILE) up -d

prod-down: ## Stop production application
	@echo "$(GREEN)Stopping production application...$(NC)"
	docker-compose -f $(COMPOSE_PROD_FILE) down

prod-logs: ## View production logs
	docker-compose -f $(COMPOSE_PROD_FILE) logs -f

# Utility commands
clean: ## Clean up Docker images and containers
	@echo "$(GREEN)Cleaning up Docker resources...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v --remove-orphans
	docker-compose -f $(COMPOSE_PROD_FILE) down -v --remove-orphans
	docker system prune -f

restart: down up ## Restart the application

status: ## Show application status
	@echo "$(GREEN)Application Status:$(NC)"
	docker-compose -f $(COMPOSE_FILE) ps

health: ## Check application health
	@echo "$(GREEN)Checking application health...$(NC)"
	@curl -f http://localhost/health && echo "$(GREEN)Frontend: OK$(NC)" || echo "$(RED)Frontend: FAIL$(NC)"
	@curl -f http://localhost/api/v1/health && echo "$(GREEN)Backend: OK$(NC)" || echo "$(RED)Backend: FAIL$(NC)"

# Database commands (for future use)
# db-migrate: ## Run database migrations
# 	docker-compose exec backend alembic upgrade head

# db-reset: ## Reset database
# 	docker-compose exec backend alembic downgrade base
# 	docker-compose exec backend alembic upgrade head