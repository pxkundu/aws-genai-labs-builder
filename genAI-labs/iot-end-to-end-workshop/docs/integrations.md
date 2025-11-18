# AWS IoT Integration Examples

This document provides examples of integrating AWS IoT with other AWS services and third-party systems.

## Integration Patterns

### 1. Amazon DynamoDB Integration

Store device metadata and state in DynamoDB.

**IoT Rule Action:**
```json
{
  "dynamoDBv2": {
    "roleArn": "arn:aws:iam::account:role/iot-dynamodb-role",
    "putItem": {
      "tableName": "iot-device-state"
    }
  }
}
```

**Lambda Function Example:**
```python
import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('iot-device-state')

def lambda_handler(event, context):
    for record in event['Records']:
        payload = json.loads(record['kinesis']['data'])
        
        table.put_item(
            Item={
                'deviceId': payload['deviceId'],
                'timestamp': payload['timestamp'],
                'temperature': payload.get('temperature'),
                'humidity': payload.get('humidity'),
                'status': payload.get('status')
            }
        )
```

### 2. Amazon SNS Integration

Send alerts via email, SMS, or push notifications.

**IoT Rule Action:**
```json
{
  "sns": {
    "targetArn": "arn:aws:sns:region:account:iot-alerts",
    "roleArn": "arn:aws:iam::account:role/iot-sns-role",
    "messageFormat": "JSON"
  }
}
```

**SNS Topic Subscription:**
```bash
aws sns subscribe \
  --topic-arn arn:aws:sns:region:account:iot-alerts \
  --protocol email \
  --notification-endpoint your-email@example.com
```

### 3. Amazon SQS Integration

Queue messages for asynchronous processing.

**IoT Rule Action:**
```json
{
  "sqs": {
    "queueUrl": "https://sqs.region.amazonaws.com/account/iot-queue",
    "roleArn": "arn:aws:iam::account:role/iot-sqs-role",
    "useBase64": false
  }
}
```

### 4. Amazon EventBridge Integration

Route IoT events to EventBridge for event-driven architectures.

**IoT Rule Action:**
```json
{
  "eventbridge": {
    "roleArn": "arn:aws:iam::account:role/iot-eventbridge-role",
    "eventBusName": "default"
  }
}
```

**EventBridge Rule:**
```json
{
  "source": ["aws.iot"],
  "detail-type": ["IoT Device Telemetry"],
  "detail": {
    "status": ["critical"]
  }
}
```

### 5. Amazon Kinesis Analytics Integration

Real-time stream processing with SQL.

**Kinesis Analytics Application:**
```sql
CREATE STREAM iot_stream (
    deviceId VARCHAR(64),
    temperature DOUBLE,
    timestamp TIMESTAMP
);

CREATE PUMP pump AS
SELECT STREAM deviceId,
       AVG(temperature) OVER WINDOW TUMBLING (SIZE 1 MINUTE) AS avg_temp
FROM iot_stream
WHERE temperature > 80;
```

### 6. Amazon QuickSight Integration

Visualize IoT data with QuickSight dashboards.

**Data Source:**
- Connect to S3 data lake
- Connect to IoT Analytics datasets
- Connect to Athena (querying S3)

**Sample QuickSight SPICE Dataset Query:**
```sql
SELECT 
    deviceId,
    DATE_TRUNC('hour', timestamp) AS hour,
    AVG(temperature) AS avg_temp,
    MAX(temperature) AS max_temp
FROM iot_telemetry
WHERE timestamp >= CURRENT_DATE - INTERVAL '7' DAY
GROUP BY deviceId, DATE_TRUNC('hour', timestamp)
```

### 7. Amazon SageMaker Integration

Machine learning inference and training.

**SageMaker Endpoint Invocation from Lambda:**
```python
import boto3
import json

sagemaker = boto3.client('sagemaker-runtime')

def lambda_handler(event, context):
    for record in event['Records']:
        payload = json.loads(record['kinesis']['data'])
        
        # Prepare features
        features = {
            'temperature': payload['temperature'],
            'humidity': payload['humidity'],
            'pressure': payload['pressure']
        }
        
        # Invoke SageMaker endpoint
        response = sagemaker.invoke_endpoint(
            EndpointName='iot-anomaly-detection',
            ContentType='application/json',
            Body=json.dumps(features)
        )
        
        prediction = json.loads(response['Body'].read())
        
        if prediction['anomaly_score'] > 0.8:
            # Trigger alert
            pass
```

### 8. Amazon Timestream Integration

Time-series database for IoT data.

**Timestream Write API:**
```python
import boto3

timestream = boto3.client('timestream-write')

def write_to_timestream(device_id, temperature, timestamp):
    timestream.write_records(
        DatabaseName='iot-db',
        TableName='telemetry',
        Records=[
            {
                'Dimensions': [
                    {'Name': 'deviceId', 'Value': device_id}
                ],
                'MeasureName': 'temperature',
                'MeasureValue': str(temperature),
                'MeasureValueType': 'DOUBLE',
                'Time': str(int(timestamp * 1000))
            }
        ]
    )
```

### 9. Amazon Redshift Integration

Data warehouse for historical analysis.

**Redshift COPY Command:**
```sql
COPY iot_telemetry
FROM 's3://iot-data-bucket/telemetry/'
IAM_ROLE 'arn:aws:iam::account:role/redshift-s3-role'
FORMAT AS JSON 'auto'
GZIP;
```

### 10. AWS Lambda@Edge Integration

Process IoT data at the edge (CloudFront).

**Use Case:** Pre-process data before sending to IoT Core.

### 11. Amazon API Gateway Integration

Expose IoT data via REST API.

**API Gateway + Lambda:**
```python
import boto3
import json

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('iot-device-state')

def lambda_handler(event, context):
    device_id = event['pathParameters']['deviceId']
    
    response = table.get_item(Key={'deviceId': device_id})
    
    return {
        'statusCode': 200,
        'body': json.dumps(response.get('Item', {}))
    }
```

### 12. Amazon ECS/Fargate Integration

Containerized processing of IoT data.

**ECS Task Definition:**
```json
{
  "family": "iot-processor",
  "containerDefinitions": [
    {
      "name": "processor",
      "image": "your-account.dkr.ecr.region.amazonaws.com/iot-processor:latest",
      "environment": [
        {"name": "KINESIS_STREAM", "value": "iot-stream"},
        {"name": "AWS_REGION", "value": "us-east-1"}
      ]
    }
  ]
}
```

### 13. AWS Step Functions Integration

Orchestrate complex IoT workflows.

**Step Functions State Machine:**
```json
{
  "Comment": "IoT Data Processing Workflow",
  "StartAt": "ProcessTelemetry",
  "States": {
    "ProcessTelemetry": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:process-telemetry",
      "Next": "CheckAnomalies"
    },
    "CheckAnomalies": {
      "Type": "Choice",
      "Choices": [
        {
          "Variable": "$.hasAnomalies",
          "BooleanEquals": true,
          "Next": "SendAlert"
        }
      ],
      "Default": "StoreData"
    },
    "SendAlert": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:send-alert",
      "Next": "StoreData"
    },
    "StoreData": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:region:account:function:store-data",
      "End": true
    }
  }
}
```

### 14. Amazon Comprehend Integration

Natural language processing for device logs.

**Comprehend Sentiment Analysis:**
```python
import boto3

comprehend = boto3.client('comprehend')

def analyze_sentiment(text):
    response = comprehend.detect_sentiment(
        Text=text,
        LanguageCode='en'
    )
    return response['Sentiment']
```

### 15. Amazon Rekognition Integration

Image analysis from IoT cameras.

**Rekognition Image Analysis:**
```python
import boto3

rekognition = boto3.client('rekognition')

def analyze_image(bucket, key):
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MaxLabels=10
    )
    return response['Labels']
```

## Third-Party Integrations

### Grafana Integration

**Data Source Configuration:**
- CloudWatch Data Source
- Timestream Data Source
- IoT Analytics Data Source

**Sample Dashboard Query:**
```sql
SELECT 
    time,
    temperature
FROM iot_telemetry
WHERE deviceId = '$device'
AND time >= now() - 1h
ORDER BY time
```

### Splunk Integration

**Splunk HEC (HTTP Event Collector):**
```python
import requests
import json

def send_to_splunk(events, hec_url, hec_token):
    headers = {
        'Authorization': f'Splunk {hec_token}',
        'Content-Type': 'application/json'
    }
    
    response = requests.post(
        f'{hec_url}/services/collector/event',
        headers=headers,
        data=json.dumps(events)
    )
    return response.status_code == 200
```

### Datadog Integration

**Datadog API:**
```python
from datadog import initialize, api

options = {
    'api_key': 'your-api-key',
    'app_key': 'your-app-key'
}

initialize(**options)

def send_metric(metric_name, value, tags):
    api.Metric.send(
        metric=metric_name,
        points=value,
        tags=tags
    )
```

## Integration Best Practices

1. **Error Handling**: Implement retry logic and dead-letter queues
2. **Monitoring**: Set up CloudWatch alarms for integration failures
3. **Security**: Use IAM roles with least privilege
4. **Cost Optimization**: Batch operations when possible
5. **Scalability**: Design for high throughput
6. **Data Validation**: Validate data before processing
7. **Documentation**: Document integration patterns and dependencies

## Additional Resources

- [AWS IoT Core Integrations](https://docs.aws.amazon.com/iot/latest/developerguide/iot-integrations.html)
- [AWS IoT Rule Actions](https://docs.aws.amazon.com/iot/latest/developerguide/iot-rule-actions.html)
- [AWS Event-Driven Architecture](https://aws.amazon.com/event-driven-architecture/)

