# Module 2: Predictive Maintenance

## Learning Objectives

By the end of this module, you will be able to:

- Configure Amazon Lookout for Equipment for anomaly detection
- Deploy SageMaker models for failure prediction
- Process real-time sensor data from Timestream
- Generate AI-powered maintenance insights with Bedrock
- Create automated maintenance work orders
- Set up alert systems for equipment failures

## Prerequisites

- Completed Module 1: Environment Setup
- AWS IoT Core configured with devices
- Timestream database with sensor data
- Access to Amazon Lookout for Equipment
- Access to Amazon SageMaker

## Duration

**Estimated Time**: 120 minutes

## Step 1: Configure Lookout for Equipment

### 1.1 Create Dataset Schema

```bash
# Create dataset schema file
cat > config/lookout-schema.json <<EOF
{
  "DatasetName": "manufacturing-equipment",
  "DatasetSchema": {
    "InferenceDataStartTime": "2024-01-01T00:00:00Z",
    "InferenceDataEndTime": "2024-12-31T23:59:59Z",
    "DataInputConfiguration": {
      "S3InputConfiguration": {
        "Bucket": "manufacturing-dev-data-lake",
        "Prefix": "lookout-training/"
      }
    },
    "DataOutputConfiguration": {
      "S3OutputConfiguration": {
        "Bucket": "manufacturing-dev-data-lake",
        "Prefix": "lookout-output/"
      }
    }
  }
}
EOF
```

### 1.2 Create Lookout Dataset

```bash
# Create dataset
aws lookout-equipment create-dataset \
  --dataset-name manufacturing-equipment \
  --dataset-schema file://config/lookout-schema.json

# Verify dataset creation
aws lookout-equipment describe-dataset \
  --dataset-name manufacturing-equipment
```

### 1.3 Import Training Data

```bash
# Upload training data to S3
aws s3 cp data/training/lookout-training-data.csv \
  s3://manufacturing-dev-data-lake/lookout-training/training-data.csv

# Import dataset
aws lookout-equipment import-dataset \
  --dataset-name manufacturing-equipment \
  --input-data-config file://config/lookout-input-config.json
```

## Step 2: Deploy SageMaker Failure Prediction Model

### 2.1 Prepare Model Training Data

```python
# prepare_training_data.py
import pandas as pd
import boto3

s3 = boto3.client('s3')

# Load historical equipment data
df = pd.read_csv('data/training/equipment-failure-data.csv')

# Prepare features
features = df[['temperature', 'vibration', 'pressure', 'power_consumption', 'runtime_hours']]
labels = df['failure_occurred']

# Save prepared data
features.to_csv('data/training/features.csv', index=False)
labels.to_csv('data/training/labels.csv', index=False)

# Upload to S3
s3.upload_file('data/training/features.csv', 
               'manufacturing-dev-data-lake', 
               'sagemaker-training/features.csv')
s3.upload_file('data/training/labels.csv', 
               'manufacturing-dev-data-lake', 
               'sagemaker-training/labels.csv')
```

### 2.2 Train SageMaker Model

```python
# train_model.py
import boto3
import sagemaker
from sagemaker.sklearn.estimator import SKLearn

sagemaker_session = sagemaker.Session()
role = 'arn:aws:iam::ACCOUNT_ID:role/SageMakerExecutionRole'

# Create estimator
estimator = SKLearn(
    entry_point='failure_prediction.py',
    role=role,
    instance_type='ml.m5.large',
    framework_version='1.0-1',
    py_version='py3',
    sagemaker_session=sagemaker_session
)

# Train model
estimator.fit({
    'training': 's3://manufacturing-dev-data-lake/sagemaker-training/'
})

# Deploy endpoint
predictor = estimator.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large',
    endpoint_name='failure-prediction-endpoint'
)
```

## Step 3: Create Predictive Maintenance Lambda

### 3.1 Implement Maintenance Function

```python
# backend/lambda/predictive-maintenance/lambda_function.py
import json
import boto3
from datetime import datetime

lookout = boto3.client('lookoutequipment')
sagemaker = boto3.client('sagemaker-runtime')
bedrock = boto3.client('bedrock-runtime')
timestream = boto3.client('timestream-query')
dynamodb = boto3.resource('dynamodb')
eventbridge = boto3.client('events')

def handler(event, context):
    """Process equipment sensor data and predict failures"""
    
    equipment_id = event['equipment_id']
    
    # Get recent sensor data from Timestream
    sensor_data = get_sensor_data(equipment_id)
    
    # Check for anomalies with Lookout
    anomalies = check_anomalies(equipment_id, sensor_data)
    
    # Get failure prediction from SageMaker
    failure_prediction = get_failure_prediction(equipment_id, sensor_data)
    
    # Generate AI insights
    insights = generate_insights(equipment_id, sensor_data, anomalies, failure_prediction)
    
    # Store health record
    store_health_record(equipment_id, sensor_data, failure_prediction)
    
    # Create maintenance recommendations
    if failure_prediction['failure_probability'] > 0.7:
        work_order = create_work_order(equipment_id, failure_prediction, insights)
        send_alert(work_order)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'equipment_id': equipment_id,
            'health_score': failure_prediction['health_score'],
            'failure_probability': failure_prediction['failure_probability'],
            'insights': insights
        })
    }

def get_sensor_data(equipment_id):
    """Query recent sensor data from Timestream"""
    query = f"""
    SELECT temperature, vibration, pressure, power_consumption
    FROM manufacturing-sensors.equipment-sensors
    WHERE equipment_id = '{equipment_id}'
    AND time >= ago(24h)
    ORDER BY time DESC
    LIMIT 100
    """
    
    response = timestream.query(QueryString=query)
    return response['Rows']

def check_anomalies(equipment_id, sensor_data):
    """Check for anomalies using Lookout for Equipment"""
    # Prepare data for Lookout
    lookout_data = prepare_lookout_data(sensor_data)
    
    # Run anomaly detection
    response = lookout.list_inference_schedulers(
        DatasetName='manufacturing-equipment'
    )
    
    if response['InferenceSchedulers']:
        scheduler_name = response['InferenceSchedulers'][0]['InferenceSchedulerName']
        anomalies = lookout.describe_inference_scheduler(
            InferenceSchedulerName=scheduler_name
        )
        return anomalies.get('Anomalies', [])
    
    return []

def get_failure_prediction(equipment_id, sensor_data):
    """Get failure prediction from SageMaker"""
    payload = {
        'equipment_id': equipment_id,
        'sensor_data': sensor_data
    }
    
    response = sagemaker.invoke_endpoint(
        EndpointName='failure-prediction-endpoint',
        ContentType='application/json',
        Body=json.dumps(payload)
    )
    
    result = json.loads(response['Body'].read())
    return result

def generate_insights(equipment_id, sensor_data, anomalies, prediction):
    """Generate AI-powered insights using Bedrock"""
    prompt = f"""
    Analyze this manufacturing equipment data:
    
    Equipment: {equipment_id}
    Health Score: {prediction['health_score']}
    Failure Probability: {prediction['failure_probability']}
    Anomalies: {len(anomalies)}
    
    Provide maintenance insights and recommendations.
    """
    
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 1000,
            'messages': [{'role': 'user', 'content': prompt}]
        })
    )
    
    result = json.loads(response['body'].read())
    return json.loads(result['content'][0]['text'])

def create_work_order(equipment_id, prediction, insights):
    """Create maintenance work order"""
    work_order = {
        'work_order_id': f"WO_{equipment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        'equipment_id': equipment_id,
        'urgency': 'high' if prediction['failure_probability'] > 0.8 else 'medium',
        'recommendations': insights.get('recommendations', []),
        'created_at': datetime.utcnow().isoformat()
    }
    
    # Store in DynamoDB
    table = dynamodb.Table('manufacturing-maintenance')
    table.put_item(Item=work_order)
    
    return work_order

def send_alert(work_order):
    """Send maintenance alert"""
    eventbridge.put_events(
        Entries=[{
            'Source': 'manufacturing.maintenance',
            'DetailType': 'Maintenance Required',
            'Detail': json.dumps(work_order)
        }]
    )
```

### 3.2 Deploy Lambda Function

```bash
# Package Lambda function
cd backend/lambda/predictive-maintenance
zip -r predictive-maintenance.zip .

# Create Lambda function
aws lambda create-function \
  --function-name manufacturing-predictive-maintenance \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_function.handler \
  --zip-file fileb://predictive-maintenance.zip \
  --timeout 60 \
  --memory-size 512
```

## Step 4: Set Up EventBridge Alerts

### 4.1 Create EventBridge Rule

```bash
# Create rule for maintenance alerts
aws events put-rule \
  --name manufacturing-maintenance-alerts \
  --event-pattern '{
    "source": ["manufacturing.maintenance"],
    "detail-type": ["Maintenance Required"]
  }'

# Add SNS topic as target
aws events put-targets \
  --rule manufacturing-maintenance-alerts \
  --targets "Id"="1","Arn"="arn:aws:sns:us-east-1:ACCOUNT_ID:maintenance-alerts"
```

## Step 5: Test Predictive Maintenance

### 5.1 Test with Sample Data

```python
# test_maintenance.py
import boto3
import json

lambda_client = boto3.client('lambda')

# Test maintenance function
response = lambda_client.invoke(
    FunctionName='manufacturing-predictive-maintenance',
    Payload=json.dumps({
        'equipment_id': 'EQ-001',
        'sensor_data': {
            'temperature': 85.5,
            'vibration': 5.2,
            'pressure': 12.8,
            'power_consumption': 18.5
        }
    })
)

result = json.loads(response['Payload'].read())
print(json.dumps(result, indent=2))
```

## Step 6: Create Monitoring Dashboard

### 6.1 Set Up CloudWatch Metrics

```python
# publish_metrics.py
import boto3

cloudwatch = boto3.client('cloudwatch')

def publish_maintenance_metrics(equipment_id, health_score, failure_probability):
    """Publish maintenance metrics to CloudWatch"""
    
    cloudwatch.put_metric_data(
        Namespace='Manufacturing/Maintenance',
        MetricData=[
            {
                'MetricName': 'EquipmentHealthScore',
                'Value': health_score,
                'Unit': 'None',
                'Dimensions': [
                    {'Name': 'EquipmentId', 'Value': equipment_id}
                ]
            },
            {
                'MetricName': 'FailureProbability',
                'Value': failure_probability,
                'Unit': 'Percent',
                'Dimensions': [
                    {'Name': 'EquipmentId', 'Value': equipment_id}
                ]
            }
        ]
    )
```

## Troubleshooting

### Issue: Lookout Dataset Import Fails

**Solution**:
1. Verify S3 bucket permissions
2. Check data format matches schema
3. Ensure sufficient training data (minimum 14 days)

### Issue: SageMaker Endpoint Not Responding

**Solution**:
1. Check endpoint status
2. Verify IAM permissions
3. Review CloudWatch logs

## Validation Checklist

Before proceeding to Module 3, verify:

- [ ] Lookout dataset created and trained
- [ ] SageMaker endpoint deployed
- [ ] Maintenance Lambda function working
- [ ] EventBridge alerts configured
- [ ] CloudWatch metrics publishing
- [ ] Test predictions working correctly

## Next Steps

Congratulations! You've completed Module 2. You're now ready to:

1. **Proceed to Module 3**: [Quality Control](./module-3-quality-control.md)
2. **Explore Advanced Features**: Customize maintenance thresholds
3. **Review Architecture**: Read the [Architecture Guide](../../architecture.md)

---

**Ready for Module 3? Let's build the quality control system! 🚀**

