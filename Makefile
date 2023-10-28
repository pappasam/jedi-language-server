.PHONY: help
help: ## Print this help menu
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: require
require: ## Check that prerequisites are installed.
	@if ! command -v python3 > /dev/null; then \
		printf "\033[1m\033[31mERROR\033[0m: python3 not installed\n" >&2 ; \
		exit 1; \
		fi
	@if ! python3 -c "import sys; sys.exit(sys.version_info < (3,8))"; then \
		printf "\033[1m\033[31mERROR\033[0m: python 3.8+ required\n" >&2 ; \
		exit 1; \
		fi
	@if ! command -v poetry > /dev/null; then \
		printf "\033[1m\033[31mERROR\033[0m: poetry not installed.\n" >&2 ; \
		printf "Please install with 'python3 -mpip install --user poetry'\n" >&2 ; \
		exit 1; \
		fi

.PHONY: setup
setup: require .setup_complete ## Set up the local development environment

.setup_complete: poetry.lock ## Internal helper to run the setup.
	poetry install
	poetry run pre-commit install
	touch .setup_complete

.PHONY: fix
fix: ## Fix all files in-place
	poetry run nox -s $@

.PHONY: lint
lint: ## Run linters on all files
	poetry run nox -s $@

.PHONY: typecheck
typecheck: ## Run static type checks
	poetry run nox -s $@

.PHONY: tests
tests: ## Run unit tests
	poetry run nox -s $@

.PHONY: publish
publish: ## Build & publish the new version
	poetry build
	poetry publish

.PHONY: clean
clean: ## Remove local development environment
	if poetry env list | grep -q Activated; then \
		poetry env remove python3; \
		fi
	rm -f .setup_complete
