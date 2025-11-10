.PHONY: all setup install run test test-coverage clean format lint help run-eval

# Make help the default target
.DEFAULT_GOAL := help

# Colors for help messages
BLUE = \033[34m
GREEN = \033[32m
YELLOW = \033[33m
WHITE = \033[37m
RESET = \033[0m

# Python version (use 3.9-3.12, numpy has issues with 3.13)
PYTHON = python3.12

# On macOS/Linux, use '.' or 'source'
VENV_ACTIVATE = . venv/bin/activate

# Help target
help:
	@echo "$(BLUE)Forgery Detection - Available Commands$(RESET)"
	@echo ""
	@echo "$(BLUE)SETUP:$(RESET)"
	@echo "  $(GREEN)clean$(WHITE)             - Clean up environment and artifacts$(RESET)"
	@echo "  $(GREEN)setup$(WHITE)             - Create virtual environment and install Poetry$(RESET)"
	@echo "  $(GREEN)install$(WHITE)           - Install project dependencies$(RESET)"
	@echo "  $(GREEN)verify$(WHITE)            - Verify installation$(RESET)"
	@echo "  $(GREEN)all$(WHITE)               - Run clean, setup, install, verify$(RESET)"
	@echo ""
	@echo "$(BLUE)DEVELOPMENT:$(RESET)"
	@echo "  $(GREEN)test$(WHITE)              - Run unit tests with pytest$(RESET)"
	@echo "  $(GREEN)test-coverage$(WHITE)     - Run tests with coverage report$(RESET)"
	@echo "  $(GREEN)format$(WHITE)            - Format code with black$(RESET)"
	@echo "  $(GREEN)lint$(WHITE)              - Lint code with ruff$(RESET)"
	@echo ""
	@echo "$(YELLOW)Examples:$(RESET)"
	@echo "  make all                          # First-time setup"
	@echo "  make test                         # Run tests"

all: clean setup install verify
	@echo ""
	@echo "$(GREEN)✓ Setup completed successfully!$(RESET)"
	@echo "$(BLUE)Virtual environment ready in 'venv/' directory$(RESET)"
	@echo "$(BLUE)Run 'make test' to run unit tests$(RESET)"
	@echo "$(BLUE)Run 'make run-eval' to test the detector$(RESET)"

clean:
	@echo "$(YELLOW)Cleaning up old environment...$(RESET)"
	rm -rf venv/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Clean complete$(RESET)"

setup:
	@echo "$(YELLOW)Creating virtual environment with $(PYTHON)...$(RESET)"
	$(PYTHON) -m venv venv
	@echo "$(YELLOW)Installing Poetry...$(RESET)"
	${VENV_ACTIVATE} && python -m pip install --upgrade pip && pip install poetry
	@echo "$(GREEN)✓ Virtual environment created$(RESET)"

install:
	@echo "$(YELLOW)Installing dependencies...$(RESET)"
	${VENV_ACTIVATE} && poetry install --with dev
	@echo "$(GREEN)✓ Dependencies installed$(RESET)"

verify:
	@echo "$(YELLOW)Verifying installation...$(RESET)"
	${VENV_ACTIVATE} && python -c "print('✓ Python virtual environment is working!')"
	@echo "$(YELLOW)Checking Poetry environment...$(RESET)"
	${VENV_ACTIVATE} && poetry env info
	@echo "$(YELLOW)Checking dependencies...$(RESET)"
	${VENV_ACTIVATE} && poetry show
	@echo "$(GREEN)✓ Verification complete$(RESET)"

test:
	@echo "$(YELLOW)Running unit tests...$(RESET)"
	${VENV_ACTIVATE} && poetry run pytest -v
	@echo "$(GREEN)✓ Tests complete$(RESET)"

test-coverage:
	@echo "$(YELLOW)Running tests with coverage...$(RESET)"
	${VENV_ACTIVATE} && poetry run pytest -v --cov=src/forgery_detection --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated in htmlcov/index.html$(RESET)"

format:
	@echo "$(YELLOW)Formatting code with black...$(RESET)"
	${VENV_ACTIVATE} && poetry run black src/ tests/
	@echo "$(GREEN)✓ Code formatted$(RESET)"

lint:
	@echo "$(YELLOW)Linting code with ruff...$(RESET)"
	${VENV_ACTIVATE} && poetry run ruff check src/ tests/
	@echo "$(GREEN)✓ Linting complete$(RESET)"


