SHELL := bash
.SHELLFLAGS := -e -x -c

# Cross-platform Bash
ifeq ($(OS),Windows_NT)
BASH := "C:/Program Files/Git/bin/bash.exe"
else
BASH := bash
endif

.PHONY: install
install: ## 🚀 Set up environment and install project
	@echo "🚀 Syncing dependencies with uv..."
	uv sync --frozen
	@echo "🔧 Installing project in editable mode..."
	uv pip install -e .

check-version:
	@echo "🔍 Checking if a Git tag exists..."
	@if git describe --tags --abbrev=0 >/dev/null 2>&1; then \
	    VERSION=$$(git describe --tags --abbrev=0); \
	    echo "✅ Git tag found: $$VERSION"; \
	else \
	    echo "❌ No Git tag found. Please create one with: git tag v0.1.0"; \
	    exit 1; \
	fi

.PHONY: check
check: ## Run all code quality checks
	@echo "🚀 Checking lock file consistency"
	uv lock --locked
	@echo "🚀 Running pre-commit hooks"
	uv run pre-commit run --all-files

.PHONY: test
test: ## Run tests using tox
	@echo "🚀 Testing code: Running tox across Python versions"
	tox

.PHONY: test-local
test-local: ## Run tests in current Python environment using uv
	@echo "🚀 Testing code locally"
	uv run python -m pytest -rvx tests --cov --cov-config=pyproject.toml --cov-report html:coverage-html

.PHONY: build
build: clean ## Build package using uv
	@echo "🚀 Building project"
	uv build

.PHONY: clean
clean: ## Clean build artifacts
	@echo "🚀 Removing build artifacts"
	rm -rf dist build *.egg-info
	rm -rf .coverage coverage-html coverage.xml .pytest_cache
	find . -name '*.pyc' -delete

.PHONY: version
version: ## Print the current project version
	uv run hatch version

.PHONY: tag
tag: ## 🏷 Tag the current release version (fixes changelog and pushes tag)
	$(BASH) scripts/tag_release.sh

.PHONY: check-dist
check-dist: ## Validate dist/ artifacts (long description, format)
	@echo "🔍 Validating dist/ artifacts..."
	uv run twine check dist/*

.PHONY: publish
publish: ## Publish to production PyPI
	@echo "🚀 Publishing to PyPI"
	UV_PUBLISH_TOKEN=$(PYPI_TOKEN) uv publish --publish-url=https://upload.pypi.org/legacy/ --no-cache

.PHONY: publish-test
publish-test: ## Publish to TestPyPI (for dry runs)
	@echo "🚀 Publishing to TestPyPI"
	UV_PUBLISH_TOKEN=$(TEST_PYPI_TOKEN) uv publish --publish-url=https://test.pypi.org/legacy/ --no-cache

.PHONY: build-and-publish
build-and-publish: build check-dist publish ## Build and publish in one step

.PHONY: help
help:
	uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.DEFAULT_GOAL := help
