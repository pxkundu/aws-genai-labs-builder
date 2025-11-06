# Makefile for Claude Code Workshop

.PHONY: help setup install test deploy clean

help:
	@echo "Claude Code Workshop - Available Commands:"
	@echo ""
	@echo "  make setup          - Set up workshop environment"
	@echo "  make install        - Install dependencies"
	@echo "  make test           - Run tests"
	@echo "  make test-unit      - Run unit tests"
	@echo "  make test-integration - Run integration tests"
	@echo "  make deploy-cdk     - Deploy with CDK"
	@echo "  make deploy-terraform - Deploy with Terraform"
	@echo "  make verify         - Verify Bedrock access"
	@echo "  make clean          - Clean up environment"
	@echo "  make cleanup        - Remove deployed infrastructure"

setup:
	@echo "🚀 Setting up workshop environment..."
	bash scripts/setup/setup_environment.sh

install:
	@echo "📦 Installing dependencies..."
	pip install --upgrade pip
	pip install -r requirements.txt

test:
	@echo "🧪 Running all tests..."
	pytest tests/ -v

test-unit:
	@echo "🧪 Running unit tests..."
	pytest tests/unit/ -v

test-integration:
	@echo "🧪 Running integration tests..."
	pytest tests/integration/ -v

deploy-cdk:
	@echo "🚀 Deploying with CDK..."
	bash scripts/deployment/deploy_cdk.sh

deploy-terraform:
	@echo "🚀 Deploying with Terraform..."
	bash scripts/deployment/deploy_terraform.sh

verify:
	@echo "🔍 Verifying Bedrock access..."
	bash scripts/setup/verify_bedrock_access.sh

clean:
	@echo "🧹 Cleaning up environment..."
	find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -r {} + 2>/dev/null || true
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov

cleanup:
	@echo "🧹 Cleaning up infrastructure..."
	bash scripts/deployment/cleanup.sh

.DEFAULT_GOAL := help

