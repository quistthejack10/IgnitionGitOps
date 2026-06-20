.PHONY: help up down lint lint-py lint-go lint-web build build-go build-web test

PY_DIRS := libs/forge-common services/api-gateway services/graph-core services/connectivity

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-12s\033[0m %s\n", $$1, $$2}'

up: ## Start infra dependencies (postgres, nats, mqtt, keycloak)
	docker compose up -d postgres nats mqtt keycloak

down: ## Stop infra
	docker compose down

lint: lint-py lint-go lint-web ## Lint everything

lint-py: ## Ruff over all Python packages
	ruff check $(PY_DIRS)

lint-go: ## go vet the flow engine
	cd flow-engine && go vet ./...

lint-web: ## Typecheck the web app
	cd web && npm run typecheck

build: build-go build-web ## Build compiled artifacts

build-go: ## Build the flow engine
	cd flow-engine && go build ./...

build-web: ## Build the web app
	cd web && npm run build

test: ## Run tests (added per component as milestones land)
	@echo "no tests yet (M0 scaffold)"

benchmark: ## Run the M1 AGE genealogy benchmark (quick mode, 100K entities)
	PYTHONPATH=services/graph-core python scripts/m1_benchmark.py --count 100000 --runs 20

benchmark-full: ## Run the real M1 spike (10M entities; allow 10-20 min)
	PYTHONPATH=services/graph-core python scripts/m1_benchmark.py --count 10000000 --runs 100

seam-test: ## Prove the Python → NATS → Go seam (requires nats + flow-engine running)
	python scripts/m1_seam_test.py
