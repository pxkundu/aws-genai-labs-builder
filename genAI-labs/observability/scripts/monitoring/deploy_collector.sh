#!/bin/bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")"/../../.. && pwd)"
LAB_DIR="$REPO_ROOT/genAI-labs/observability"
COLLECTOR_IMAGE="public.ecr.aws/aws-observability/aws-otel-collector:latest"

cat <<EOF > "$LAB_DIR/config/templates/adot-collector.yaml"
receivers:
  otlp:
    protocols:
      grpc:
      http:
exporters:
  awsxray:
  awsemf:
  awscloudwatchlogs:
    log_group_name: /aws/observability/${ENVIRONMENT:-dev}-genai-observability
service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [awsxray]
    metrics:
      receivers: [otlp]
      exporters: [awsemf]
    logs:
      receivers: [otlp]
      exporters: [awscloudwatchlogs]
EOF

echo "🔄 Starting ADOT Collector container"
docker run -d --name adot-collector \
  -p 4317:4317 -p 4318:4318 \
  -e AWS_REGION=${AWS_REGION:-us-east-1} \
  -e AWS_PROFILE=${AWS_PROFILE:-default} \
  -v "$LAB_DIR/config/templates/adot-collector.yaml":/otel-local-config.yaml \
  "$COLLECTOR_IMAGE" --config otel-local-config.yaml

echo "✅ Collector running. Point OTEL_EXPORTER_OTLP_ENDPOINT to http://localhost:4318"
