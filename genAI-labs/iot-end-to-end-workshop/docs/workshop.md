## Workshop: AWS IoT End-to-End

This workshop guides you through provisioning, connecting, ingesting, analyzing, and responding to IoT device data on AWS using Terraform. Complete the sections in order.

Prereqs:

- Terraform >= 1.5, AWS CLI v2, jq
- A dedicated AWS account with admin access
- mosquitto-clients (optional, for quick MQTT tests) or any MQTT client

Environment setup:

```bash
aws sts get-caller-identity
aws configure list
terraform -version
```

### 1) Deploy infrastructure

```bash
cd infrastructure/terraform
cp terraform.tfvars.example terraform.tfvars
# edit terraform.tfvars (project_name, region, and optional flags)
terraform init
terraform apply -auto-approve
```

Outputs include:

- IoT endpoint, IoT policy name, S3 bucket for raw data, Kinesis stream name, Lambda ARN, IoT Analytics resources, IoT Events detector name.

### 2) Device identity: certificates and policy

Option A: Use Fleet Provisioning (template created by Terraform).

Option B: Manual certificate (quick local sim):

```bash
# Create keys and certificate (ACTIVE). Save the outputs.
aws iot create-keys-and-certificate --set-as-active > cert.json
jq -r .certificatePem cert.json > deviceCert.pem.crt
jq -r .keyPair.PrivateKey cert.json > privateKey.pem.key
jq -r .certificateArn cert.json

# Download AmazonRootCA1 (once)
curl -o AmazonRootCA1.pem https://www.amazontrust.com/repository/AmazonRootCA1.pem

# Attach the Terraform-created IoT policy to the cert
POLICY_NAME=$(terraform output -raw iot_policy_name)
CERT_ARN=$(jq -r .certificateArn cert.json)
aws iot attach-policy --policy-name "$POLICY_NAME" --target "$CERT_ARN"

# Create a Thing (optional but recommended) and attach cert to thing
THING_NAME="myThing"
aws iot create-thing --thing-name "$THING_NAME" || true
aws iot attach-thing-principal --thing-name "$THING_NAME" --principal "$CERT_ARN"
```

Notes:

- The provided policy allows basic connect/publish/subscribe for workshop topics. Adjust for least-privilege in production.

### 3) Provision a device (Fleet Provisioning template)

The stack creates a Fleet Provisioning template for Just-In-Time provisioning.

Flow overview (conceptual):

1. Device uses a bootstrap/claim certificate to call CreateKeysAndCertificate and RegisterThing against the template.
2. IoT Core creates the Thing, activates a new cert, and attaches the device policy.
3. Device stores the returned device certificate and connects using it going forward.

You can simulate with a bootstrap/claim cert, or skip to manual registration if preferred.

### 4) Connect and publish telemetry (simulate)

Discover your endpoint and publish a sample payload:

```bash
aws iot describe-endpoint --endpoint-type iot:Data-ATS

# Example using mosquitto_pub (requires device certs)
mosquitto_pub -h <iot_endpoint> -p 8883 \
  --cafile AmazonRootCA1.pem \
  --cert deviceCert.pem.crt \
  --key privateKey.pem.key \
  -t "devices/myThing/telemetry" \
  -m '{"ts": 1731715200, "tempC": 28.5, "humidity": 42, "status":"ok"}'
```

### 5) Inspect data flow

- Kinesis Data Streams receives raw telemetry (Rule 1).
- Firehose archives to S3 data lake (Rule 2).
- Lambda processor can enrich or route to alerts stream (Rule 3).

Check:

- CloudWatch Logs for Lambda
- S3 bucket for objects under `/year=.../month=.../day=.../`
- Kinesis metrics for incoming records

Optional quick checks via CLI:

```bash
# Identify resources
KINESIS_STREAM=$(terraform output -raw kinesis_stream_name)
S3_BUCKET=$(terraform output -raw firehose_bucket_name)

# List S3 prefixes created by Firehose
aws s3 ls "s3://${S3_BUCKET}/" --recursive --human-readable --summarize | head -n 50

# Peek Kinesis metrics (requires CloudWatch get-metric-data; or view console)
aws cloudwatch get-metric-statistics \
  --namespace AWS/Kinesis \
  --metric-name IncomingRecords \
  --dimensions Name=StreamName,Value="$KINESIS_STREAM" \
  --start-time "$(date -u -v-15M +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '15 minutes ago' +%Y-%m-%dT%H:%M:%SZ)" \
  --end-time "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --period 60 \
  --statistics Sum
```

### 6) IoT Analytics (channel, pipeline, datastore, dataset)

The Terraform stack wires `IoT Analytics` to ingest from Kinesis.

- Query datasets from the console or CLI:

```bash
aws iotanalytics list-datasets
aws iotanalytics get-dataset-content --dataset-name <name>
```

### 7) IoT Events (input + detector model)

Device messages are mirrored to IoT Events input. The detector model evaluates conditions (e.g., temperature threshold).

Try sending an over-threshold message and observe detector state transitions and the optional SNS notification.

Example (tempC > 35 triggers alarm state):

```bash
mosquitto_pub -h <iot_endpoint> -p 8883 \
  --cafile AmazonRootCA1.pem \
  --cert deviceCert.pem.crt \
  --key privateKey.pem.key \
  -t "devices/myThing/telemetry" \
  -m '{"deviceId":"myThing","tempC": 40, "status":"hot"}'
```

### 8) Device Shadows

Publish to shadow update topics to observe desired/reported state sync:

```bash
mosquitto_pub -h <iot_endpoint> -p 8883 \
  --cafile AmazonRootCA1.pem \
  --cert deviceCert.pem.crt \
  --key privateKey.pem.key \
  -t "\$aws/things/myThing/shadow/update" \
  -m '{"state": {"desired": {"fan": "on"}}}'
```

Read back the shadow:

```bash
mosquitto_sub -h <iot_endpoint> -p 8883 \
  --cafile AmazonRootCA1.pem \
  --cert deviceCert.pem.crt \
  --key privateKey.pem.key \
  -t "\$aws/things/myThing/shadow/get/accepted" &

mosquitto_pub -h <iot_endpoint> -p 8883 \
  --cafile AmazonRootCA1.pem \
  --cert deviceCert.pem.crt \
  --key privateKey.pem.key \
  -t "\$aws/things/myThing/shadow/get" -m '{}'
```

### 9) Device Defender posture

The stack enables a sample security profile monitoring behaviors (e.g., message rates). Review Defender metrics and findings in the console.

To simulate a violation, publish at a high rate for a few minutes, then review findings:

```bash
for i in $(seq 1 200); do
  mosquitto_pub -h <iot_endpoint> -p 8883 \
    --cafile AmazonRootCA1.pem \
    --cert deviceCert.pem.crt \
    --key privateKey.pem.key \
    -t "devices/myThing/telemetry" \
    -m "{\"deviceId\":\"myThing\",\"tempC\": 25, \"seq\": $i}"
done
```

### 10) Observability

CloudWatch dashboards include:

- Ingestion metrics (IoT Core, Kinesis, Firehose)
- Lambda errors and duration
- S3 delivery metrics

Identify the dashboard name (based on your `project_name`/region) in the CloudWatch console.

### 11) Optional: MQTT over WebSocket (no device certs)

If you prefer using SigV4 with WebSockets (e.g., from a browser), you can use the AWS IoT Test Console’s MQTT client or SDKs. Ensure the connected IAM principal allows `iot:Connect`, `iot:Publish`, `iot:Subscribe`, `iot:Receive` for your test topics.

### 12) Cleanup

```bash
cd infrastructure/terraform
terraform destroy -auto-approve
```

### Troubleshooting

- Ensure device certs are valid and policy allows required topics.
- Verify IoT endpoint is `Data-ATS`.
- Check CloudWatch Logs for Lambda and Firehose delivery errors.
- Check that your local time is correct (TLS/expiry issues).
- If mosquitto errors with TLS, ensure `AmazonRootCA1.pem` matches the endpoint CA.
- For Kinesis errors, confirm stream name and region match outputs.


