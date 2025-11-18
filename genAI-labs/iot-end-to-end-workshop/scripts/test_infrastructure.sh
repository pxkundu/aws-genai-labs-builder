#!/bin/bash
#
# Infrastructure Testing Script
#
# Tests the deployed AWS IoT infrastructure by:
# 1. Verifying all resources exist
# 2. Testing IoT Core connectivity
# 3. Validating data flow through the pipeline
# 4. Checking CloudWatch metrics
#

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_NAME="${PROJECT_NAME:-iot-workshop}"
REGION="${AWS_REGION:-us-east-1}"

echo -e "${GREEN}=== AWS IoT Infrastructure Testing ===${NC}\n"

# Function to check if resource exists
check_resource() {
    local resource_type=$1
    local resource_name=$2
    local check_cmd=$3
    
    echo -n "Checking ${resource_type} '${resource_name}'... "
    if eval "$check_cmd" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC}"
        return 0
    else
        echo -e "${RED}✗${NC}"
        return 1
    fi
}

# 1. Verify IoT Core Resources
echo -e "${YELLOW}1. Verifying IoT Core Resources${NC}"
check_resource "IoT Endpoint" "data-ats" \
    "aws iot describe-endpoint --endpoint-type iot:Data-ATS --region ${REGION}"

check_resource "IoT Policy" "${PROJECT_NAME}-device-policy" \
    "aws iot get-policy --policy-name ${PROJECT_NAME}-device-policy --region ${REGION}"

check_resource "Thing Type" "${PROJECT_NAME}-sensor" \
    "aws iot describe-thing-type --thing-type-name ${PROJECT_NAME}-sensor --region ${REGION}"

# 2. Verify Streaming Resources
echo -e "\n${YELLOW}2. Verifying Streaming Resources${NC}"
KINESIS_STREAM="${PROJECT_NAME}-${REGION}-telemetry-stream"
check_resource "Kinesis Stream" "${KINESIS_STREAM}" \
    "aws kinesis describe-stream --stream-name ${KINESIS_STREAM} --region ${REGION}"

FIREHOSE_STREAM="${PROJECT_NAME}-${REGION}-firehose"
check_resource "Kinesis Firehose" "${FIREHOSE_STREAM}" \
    "aws firehose describe-delivery-stream --delivery-stream-name ${FIREHOSE_STREAM} --region ${REGION}"

S3_BUCKET="${PROJECT_NAME}-${REGION}-iot-data"
check_resource "S3 Bucket" "${S3_BUCKET}" \
    "aws s3 ls s3://${S3_BUCKET} --region ${REGION}"

# 3. Verify Lambda Function
echo -e "\n${YELLOW}3. Verifying Lambda Function${NC}"
LAMBDA_FUNCTION="${PROJECT_NAME}-${REGION}-processor"
check_resource "Lambda Function" "${LAMBDA_FUNCTION}" \
    "aws lambda get-function --function-name ${LAMBDA_FUNCTION} --region ${REGION}"

# 4. Verify IoT Analytics
echo -e "\n${YELLOW}4. Verifying IoT Analytics${NC}"
ANALYTICS_CHANNEL="${PROJECT_NAME}-${REGION}-channel"
check_resource "IoT Analytics Channel" "${ANALYTICS_CHANNEL}" \
    "aws iotanalytics describe-channel --channel-name ${ANALYTICS_CHANNEL} --region ${REGION}"

ANALYTICS_DATASET="${PROJECT_NAME}-${REGION}-dataset"
check_resource "IoT Analytics Dataset" "${ANALYTICS_DATASET}" \
    "aws iotanalytics describe-dataset --dataset-name ${ANALYTICS_DATASET} --region ${REGION}"

# 5. Verify IoT Events
echo -e "\n${YELLOW}5. Verifying IoT Events${NC}"
EVENTS_INPUT="${PROJECT_NAME}-${REGION}-input"
check_resource "IoT Events Input" "${EVENTS_INPUT}" \
    "aws iotevents describe-input --input-name ${EVENTS_INPUT} --region ${REGION}"

EVENTS_DETECTOR="${PROJECT_NAME}-${REGION}-detector"
check_resource "IoT Events Detector" "${EVENTS_DETECTOR}" \
    "aws iotevents describe-detector-model --detector-model-name ${EVENTS_DETECTOR} --region ${REGION}"

# 6. Verify Device Defender
echo -e "\n${YELLOW}6. Verifying Device Defender${NC}"
DEFENDER_PROFILE="${PROJECT_NAME}-${REGION}-security-profile"
check_resource "Device Defender Profile" "${DEFENDER_PROFILE}" \
    "aws iot describe-security-profile --security-profile-name ${DEFENDER_PROFILE} --region ${REGION}"

# 7. Verify CloudWatch Dashboard
echo -e "\n${YELLOW}7. Verifying CloudWatch Dashboard${NC}"
DASHBOARD_NAME="${PROJECT_NAME}-${REGION}-dashboard"
check_resource "CloudWatch Dashboard" "${DASHBOARD_NAME}" \
    "aws cloudwatch get-dashboard --dashboard-name ${DASHBOARD_NAME} --region ${REGION}"

# 8. Test IoT Rules
echo -e "\n${YELLOW}8. Verifying IoT Rules${NC}"
RULE_NAMES=(
    "${PROJECT_NAME}-${REGION}-rule-kinesis"
    "${PROJECT_NAME}-${REGION}-rule-firehose"
    "${PROJECT_NAME}-${REGION}-rule-lambda"
    "${PROJECT_NAME}-${REGION}-rule-events"
)

for rule_name in "${RULE_NAMES[@]}"; do
    check_resource "IoT Rule" "${rule_name}" \
        "aws iot get-topic-rule --rule-name ${rule_name} --region ${REGION}"
done

# 9. Check CloudWatch Metrics
echo -e "\n${YELLOW}9. Checking CloudWatch Metrics${NC}"
echo -n "Checking IoT Core message count... "
METRIC_COUNT=$(aws cloudwatch get-metric-statistics \
    --namespace AWS/IoT \
    --metric-name NumberOfMessagesPublished \
    --dimensions Name=ThingName,Value=test \
    --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
    --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
    --period 3600 \
    --statistics Sum \
    --region ${REGION} \
    --query 'Datapoints[0].Sum' \
    --output text 2>/dev/null || echo "0")

if [ "${METRIC_COUNT}" != "None" ] && [ "${METRIC_COUNT}" != "0" ]; then
    echo -e "${GREEN}✓ (${METRIC_COUNT} messages)${NC}"
else
    echo -e "${YELLOW}⚠ (no recent messages)${NC}"
fi

# 10. Test S3 Data Delivery
echo -e "\n${YELLOW}10. Checking S3 Data Delivery${NC}"
echo -n "Checking for recent S3 objects... "
RECENT_OBJECTS=$(aws s3 ls s3://${S3_BUCKET} --recursive --region ${REGION} 2>/dev/null | wc -l)
if [ "${RECENT_OBJECTS}" -gt 0 ]; then
    echo -e "${GREEN}✓ (${RECENT_OBJECTS} objects found)${NC}"
else
    echo -e "${YELLOW}⚠ (no objects yet - publish some messages first)${NC}"
fi

# Summary
echo -e "\n${GREEN}=== Testing Complete ===${NC}"
echo "All critical resources verified."
echo ""
echo "Next steps:"
echo "1. Use device_simulator.py to publish test messages"
echo "2. Check CloudWatch dashboard for metrics"
echo "3. Query IoT Analytics datasets"
echo "4. Verify data in S3 bucket"

