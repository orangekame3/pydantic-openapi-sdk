.PHONY: help install test test-local test-real-api ci-test clean lint format check dev generate-sdk download-spec generate-local-spec

# Variables
SPEC_URL = https://petstore3.swagger.io/api/v3/openapi.json
SPEC_FILE = petstore3_openapi.json

help: ## Show this help message
	@echo "🐕 Pydantic OpenAPI SDK Generator"
	@echo "================================="
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Install dependencies
	uv sync

dev: install ## Set up development environment
	uv run pre-commit install
	@echo "✅ Development environment ready!"

test: ## Run basic tests (requires existing SDK)
	@echo "🧪 Running basic SDK tests..."
	uv run python examples/test_petstore_client.py

generate-sdk: ## Generate SDK from config without downloading spec
	@echo "⚙️  Generating SDK from configuration..."
	uv run pydantic-openapi-sdk generate --config configs/petstore.yaml --verbose

download-spec: ## Download OpenAPI specification
	@echo "📥 Downloading OpenAPI specification..."
	curl -f -s -o $(SPEC_FILE) $(SPEC_URL)
	@if command -v jq >/dev/null 2>&1; then \
		echo "   Title: $$(jq -r '.info.title' $(SPEC_FILE))"; \
		echo "   Version: $$(jq -r '.info.version' $(SPEC_FILE))"; \
		echo "   Tags: $$(jq -r '.tags[].name' $(SPEC_FILE) | tr '\n' ',' | sed 's/,$$//')"; \
	fi

test-local: generate-sdk test ## Generate SDK and run tests locally

ci-test: install download-spec generate-sdk test check ## Full CI test pipeline

test-real-api: clean download-spec generate-local-spec test ## Download OpenAPI spec, generate SDK, and test against real API
	@echo "✅ Real API test completed successfully!"

generate-local-spec: ## Generate SDK using downloaded spec file
	@echo "🧹 Cleaning up previous SDK..."
	rm -rf examples/gen/petstore_sdk
	@echo "⚙️  Generating SDK from downloaded spec..."
	uv run pydantic-openapi-sdk generate \
		--config configs/petstore.yaml \
		--spec $(SPEC_FILE) \
		--verbose

lint: ## Run linting
	uv run ruff check .

format: ## Format code
	uv run ruff format .

check: lint format ## Run all code quality checks
	uv run ruff check .
	@echo "✅ Code quality checks passed!"

clean: ## Clean up generated files and caches
	rm -rf examples/gen/petstore_sdk
	rm -f $(SPEC_FILE)
	rm -rf .pytest_cache
	rm -rf __pycache__
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "✅ Cleaned up!"

# Continuous testing commands
watch-api: ## Watch for API changes (requires entr)
	@if ! command -v entr >/dev/null 2>&1; then \
		echo "❌ 'entr' is required for watching. Install with: brew install entr"; \
		exit 1; \
	fi
	@echo "👀 Watching for changes... (Ctrl+C to stop)"
	@echo "Will re-test every 60 seconds"
	while true; do \
		make test-real-api; \
		sleep 60; \
	done

demo: test-real-api ## Run full demo (alias for test-real-api)

# Help target (default)
.DEFAULT_GOAL := help
