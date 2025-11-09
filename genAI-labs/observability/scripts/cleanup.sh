#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../.. && pwd)"
LAB_DIR="$REPO_ROOT/observability"

cd "$LAB_DIR/infrastructure/terraform"

echo "🧹 Destroying observability stack"
terraform destroy "$@"
