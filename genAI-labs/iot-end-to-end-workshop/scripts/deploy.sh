#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TF_DIR="${SCRIPT_DIR}/../infrastructure/terraform"

cd "$TF_DIR"
terraform init
terraform apply -auto-approve

echo "Deployed. Outputs:"
terraform output


