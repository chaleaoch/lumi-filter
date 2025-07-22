.PHONY: test test-cov test-cov-html clean install dev-install lint format check

# Install dependencies
install:
	uv sync

# Install development dependencies
dev-install:
	uv sync --dev

# Run tests
test:
	uv run pytest

# Run tests with coverage
test-cov:
	uv run pytest --cov=lumi_filter

# Run tests with coverage and generate HTML report
test-cov-html:
	uv run pytest --cov=lumi_filter --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

# Run tests with all coverage reports
test-cov-all:
	uv run pytest --cov=lumi_filter --cov-report=term-missing --cov-report=html --cov-report=xml

# Clean up generated files
clean:
	rm -rf htmlcov/
	rm -f coverage.xml
	rm -rf .coverage
	rm -rf .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

# Lint code
lint:
	uv run ruff check .

# Format code
format:
	uv run ruff format .

# Check code quality
check: lint test-cov

# Run specific test file
test-file:
	@if [ -z "$(FILE)" ]; then \
		echo "Usage: make test-file FILE=path/to/test_file.py"; \
	else \
		uv run pytest $(FILE) -v; \
	fi

# Run tests for specific module
test-module:
	@if [ -z "$(MODULE)" ]; then \
		echo "Usage: make test-module MODULE=module_name"; \
	else \
		uv run pytest tests/test_$(MODULE).py -v; \
	fi

# Show coverage report without running tests
show-cov:
	uv run coverage report --show-missing

# Generate HTML coverage report without running tests
show-cov-html:
	uv run coverage html
	@echo "Coverage report available at htmlcov/index.html"

# Help
help:
	@echo "Available commands:"
	@echo "  install      - Install dependencies"
	@echo "  dev-install  - Install development dependencies"
	@echo "  test         - Run tests"
	@echo "  test-cov     - Run tests with coverage"
	@echo "  test-cov-html - Run tests with HTML coverage report"
	@echo "  test-cov-all - Run tests with all coverage reports"
	@echo "  test-file    - Run specific test file (use FILE=path)"
	@echo "  test-module  - Run tests for specific module (use MODULE=name)"
	@echo "  clean        - Clean up generated files"
	@echo "  lint         - Run linter"
	@echo "  format       - Format code"
	@echo "  check        - Run linter and tests with coverage"
	@echo "  show-cov     - Show coverage report"
	@echo "  show-cov-html - Generate HTML coverage report"
	@echo "  help         - Show this help message"
