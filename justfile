# Justfile for octowalrus project
# Run with: just <command>

# Variables
namespace := "default"
context := "docker-desktop"
tilt_port := "10351"

# Default target
default:
    @just --list

# Check if docker is installed
_check-docker:
    #!/usr/bin/env bash
    if ! command -v docker &> /dev/null; then
        echo "Error: docker is not installed. Please install docker first."
        exit 1
    fi

# Check if kubectl is installed
_check-kubectl:
    #!/usr/bin/env bash
    if ! command -v kubectl &> /dev/null; then
        echo "Error: kubectl is not installed. Please install kubectl first."
        echo "refer to .tool-versions or visit: https://kubernetes.io/docs/tasks/tools/"
        exit 1
    fi

_with-context: _check-kubectl
    #!/usr/bin/env bash
    if ! kubectl config get-contexts {{context}} &> /dev/null; then
        echo "Error: context {{context}} is not found. Please check your kubeconfig file."
        exit 1
    fi
    
    if ! kubectl config use-context {{context}}; then
        echo "Error: Failed to switch to context {{context}}"
        exit 1
    fi
    
_check-namespace: _with-context
    #!/usr/bin/env bash
    if ! kubectl get namespace {{namespace}} &> /dev/null; then
        echo "Warning: namespace {{namespace}} does not exist. Creating it..."
        if ! kubectl create namespace {{namespace}}; then
            echo "Error: Failed to create namespace {{namespace}}"
            exit 1
        fi
    fi

# Check if tilt is installed
_check-tilt: _check-docker _with-context _check-namespace
    #!/usr/bin/env bash
    if ! command -v tilt &> /dev/null; then
        echo "Error: tilt is not installed. Please install tilt first."
        echo "Visit: https://docs.tilt.dev/install.html"
        exit 1
    fi
    
    if ! command -v helm &> /dev/null; then
        echo "Error: helm is not installed. Please install helm first."
        echo "Visit: https://helm.sh/docs/intro/install/"
        exit 1
    fi

_check-env:
    #!/usr/bin/env bash
    env_vars="GRAFANA_API_KEY GRAFANA_API_URL=https://sample-grafana-api-url"
    # replace commas with spaces
    env_vars="${env_vars//,/ }"
    # trim whitespace
    env_vars=$(echo "$env_vars" | xargs)
    
    if [ -z "$env_vars" ]; then
        echo "✅ No environment variables to check"
        exit 0
    fi
    
    missing_vars=()
    
    for pair in $env_vars; do
        # Trim whitespace
        pair=$(echo "$pair" | xargs)
        
        # Extract variable name (everything before '=' if present)
        if [[ "$pair" == *"="* ]]; then
            var="${pair%%=*}"
        else
            var="$pair"
        fi
        
        # Check if variable is set
        if [ -n "$var" ] && [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -gt 0 ]; then
        echo "❌ Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "   - $var"
        done
        echo ""
        echo "Please ensure these variables are set in your environment."
        echo "👀 Create a .env file from env.example: cp .env.example .env"
        echo "  NOTE: override defaults as desired"
        exit 1
    else
        echo "✅ All required environment variables are set"
    fi

# lifecycle hook called by other justfiles
hook-post-git-init:
    @echo "Handling all functions for post git initialization..."

# Development commands
dev: _check-tilt
    tilt up --port 10300

dev-stop: _check-tilt
    tilt down

# Build commands
build: _check-docker
    docker build -t octowalrus-app:latest .

build-dev: _check-docker
    docker build --target development -t octowalrus-app:dev .

# Test commands
test:
    pytest

test-watch:
    pytest --watch

test-coverage:
    pytest --cov=octowalrus --cov-report=html

# Linting and formatting
lint:
    black src/ tests/
    isort src/ tests/
    flake8 src/ tests/

lint-check:
    black --check src/ tests/
    isort --check-only src/ tests/
    flake8 src/ tests/

# Type checking
type-check:
    uv run mypy src/

# Pre-commit
pre-commit: pre-commit-install
    uv run pre-commit run --all-files

@pre-commit-install: install-dev
    uv run pre-commit install

# Clean up
clean:
    find . -type f -name "*.pyc" -delete
    find . -type d -name "__pycache__" -delete
    find . -type d -name "*.egg-info" -exec rm -rf {} +
    rm -rf .pytest_cache/
    rm -rf htmlcov/
    rm -rf .coverage

# Install dependencies
install:
    uv sync

install-dev:
    uv sync --extra dev

# Run the application locally
run:
    uvicorn octowalrus.main:app --reload --host 0.0.0.0 --port 8000

# Debug mode
debug:
    python -m debugpy --listen 0.0.0.0:5678 --wait-for-client -m uvicorn octowalrus.main:app --reload --host 0.0.0.0 --port 8000 