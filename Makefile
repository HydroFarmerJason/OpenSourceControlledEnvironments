# Container Farm Control System Makefile

.PHONY: help install test clean setup-dev lint format

help:
@echo "Container Farm Control System"
@echo "Available commands:"
@echo "  install    - Install system dependencies and setup"
@echo "  test       - Run all tests"
@echo "  setup-dev  - Setup development environment"
@echo "  lint       - Run code linting"
@echo "  format     - Format code"
@echo "  clean      - Clean temporary files"

install:
@echo "Installing Container Farm Control System..."
sudo ./setup/setup.sh

test:
@echo "Running tests..."
python -m pytest tests/ -v

setup-dev:
@echo "Setting up development environment..."
python -m venv venv
. venv/bin/activate && pip install -r requirements.txt
. venv/bin/activate && pip install -r setup/dependencies/dev_requirements.txt

lint:
@echo "Running linting..."
flake8 src/ tests/
black --check src/ tests/

format:
@echo "Formatting code..."
black src/ tests/
isort src/ tests/

clean:
@echo "Cleaning temporary files..."
find . -type f -name "*.pyc" -delete
find . -type d -name "__pycache__" -delete
rm -rf build/ dist/ *.egg-info/
rm -rf .pytest_cache/ .coverage htmlcov/
