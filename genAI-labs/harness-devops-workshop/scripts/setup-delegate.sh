#!/bin/bash

# Harness Delegate Installation Script
# This script installs the Harness Delegate on Docker

set -e

echo "========================================="
echo "Harness Delegate Installation"
echo "========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo "Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Prompt for Harness account details
read -p "Enter your Harness Account ID: " ACCOUNT_ID
read -p "Enter your Harness Delegate Token: " DELEGATE_TOKEN
read -p "Enter Delegate Name (default: workshop-delegate): " DELEGATE_NAME
DELEGATE_NAME=${DELEGATE_NAME:-workshop-delegate}

echo ""
echo "Installing Harness Delegate..."
echo "Account ID: $ACCOUNT_ID"
echo "Delegate Name: $DELEGATE_NAME"
echo ""

# Stop and remove existing delegate if it exists
if docker ps -a | grep -q "$DELEGATE_NAME"; then
    echo "Stopping existing delegate..."
    docker stop "$DELEGATE_NAME" || true
    docker rm "$DELEGATE_NAME" || true
fi

# Run Harness Delegate
docker run --cpus=1 --memory=2g \
  -e DELEGATE_NAME="$DELEGATE_NAME" \
  -e NEXT_GEN=true \
  -e DELEGATE_TYPE=DOCKER \
  -e ACCOUNT_ID="$ACCOUNT_ID" \
  -e DELEGATE_TOKEN="$DELEGATE_TOKEN" \
  -e MANAGER_HOST_AND_PORT=https://app.harness.io \
  -e POLL_FOR_TASKS=true \
  -e HELM_DESIRED_VERSION= \
  -e WATCHER_STORAGE_URL=https://app.harness.io/public/free/free-tier-watcher \
  -e WATCHER_CHECK_LOCATION=watcherci.txt \
  -e DELEGATE_STORAGE_URL=https://app.harness.io/public/free/free-tier-delegate \
  -e DELEGATE_CHECK_LOCATION=delegateci.txt \
  -e DEPLOY_MODE=KUBERNETES \
  -e PROXY_HOST= \
  -e PROXY_PORT= \
  -e PROXY_SCHEME= \
  -e PROXY_USER= \
  -e PROXY_PASSWORD= \
  -e NO_PROXY= \
  -e PROXY_MANAGER=true \
  -e INIT_SCRIPT= \
  --name "$DELEGATE_NAME" \
  harness/delegate:latest

echo ""
echo "========================================="
echo "Delegate installation complete!"
echo "========================================="
echo ""
echo "Delegate Name: $DELEGATE_NAME"
echo "Container Status:"
docker ps | grep "$DELEGATE_NAME" || echo "Container is starting..."
echo ""
echo "To view logs: docker logs -f $DELEGATE_NAME"
echo "To stop delegate: docker stop $DELEGATE_NAME"
echo "To remove delegate: docker rm $DELEGATE_NAME"
echo ""
echo "Wait 2-3 minutes for the delegate to register in Harness."
echo "Check the Harness UI to verify connection status."

