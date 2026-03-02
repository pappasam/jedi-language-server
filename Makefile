.PHONY: help
help: ## Print this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: require
require: ## Check that prerequisites are installed.
	@if ! command -v uv > /dev/null; then \
		printf "\033[1m\033[31mERROR\033[0m: uv not installed.\n" >&2 ; \
		printf "Please install with 'curl -LsSf https://astral.sh/uv/install.sh | sh'\n" >&2 ; \
		exit 1; \
		fi

.PHONY: setup
setup: require .setup_complete ## Set up the local development environment

.setup_complete: uv.lock ## Internal helper to run the setup.
	uv sync --group dev
	uv run pre-commit install
	touch .setup_complete

.PHONY: fix
fix: ## Fix all files in-place
	uv run nox -s $@

.PHONY: lint
lint: ## Run linters on all files
	uv run nox -s $@

.PHONY: typecheck
typecheck: ## Run static type checks
	uv run nox -s $@

.PHONY: tests
tests: ## Run unit tests
	uv run nox -s $@

.PHONY: publish
publish: ## Build & publish the new version
	uv build
	uv publish

.PHONY: clean
clean: ## Remove local development environment
	rm -rf .venv .setup_complete
