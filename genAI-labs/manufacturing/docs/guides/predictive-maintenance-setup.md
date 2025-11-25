# Predictive Maintenance Setup Guide

## Overview

This guide provides detailed instructions for setting up and configuring the AI-powered predictive maintenance system for manufacturing equipment. The system combines Amazon Lookout for Equipment, Amazon SageMaker, and Amazon Bedrock to deliver real-time equipment health monitoring and failure prediction.

## Architecture

The predictive maintenance system consists of:

1. **Data Ingestion**: IoT Core and Timestream for sensor data
2. **Anomaly Detection**: Lookout for Equipment for real-time anomalies
3. **Failure Prediction**: SageMaker ML models for failure prediction
4. **GenAI Insights**: Bedrock for maintenance recommendations
5. **Alert System**: EventBridge for maintenance alerts
6. **Storage**: DynamoDB for maintenance records

## Prerequisites

- AWS Account with required services enabled
- Bedrock model access configured
- Lookout for Equipment access
- SageMaker endpoint deployed (or use pre-built models)
- Timestream database configured
- IoT Core devices connected
- DynamoDB tables created

## Step 1: Deploy Infrastructure

### 1.1 Configure Lookout for Equipment

```bash
# Create dataset schema
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

# Create dataset
aws lookout-equipment create-dataset \
  --dataset-name manufacturing-equipment \
  --dataset-schema file://config/lookout-schema.json
```

### 1.2 Create DynamoDB Tables

```bash
# Maintenance records table
aws dynamodb create-table \
  --table-name manufacturing-maintenance \
  --attribute-definitions \
    AttributeName=work_order_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=work_order_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# Equipment health table
aws dynamodb create-table \
  --table-name manufacturing-equipment-health \
  --attribute-definitions \
    AttributeName=equipment_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=equipment_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
```

## Step 2: Deploy Lambda Functions

### 2.1 Create Maintenance Lambda

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
  --memory-size 512 \
  --environment Variables={
    LOOKOUT_DATASET=manufacturing-equipment,
    SAGEMAKER_ENDPOINT=failure-prediction-endpoint,
    BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0,
    TIMESTREAM_DB=manufacturing-sensors,
    TIMESTREAM_TABLE=equipment-sensors
  }
```

### 2.2 Configure Timestream Trigger

```bash
# Create EventBridge rule for Timestream
aws events put-rule \
  --name manufacturing-maintenance-trigger \
  --event-pattern '{
    "source": ["aws.timestream"],
    "detail-type": ["Timestream Query State Change"]
  }'

# Add Lambda as target
aws events put-targets \
  --rule manufacturing-maintenance-trigger \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-1:ACCOUNT_ID:function:manufacturing-predictive-maintenance"
```

## Step 3: Configure SageMaker Endpoint

### 3.1 Deploy Failure Prediction Model

```python
# deploy_failure_model.py
import boto3
import sagemaker
from sagemaker.model import Model
from sagemaker.predictor import Predictor

sagemaker_session = sagemaker.Session()
role = 'arn:aws:iam::ACCOUNT_ID:role/SageMakerExecutionRole'

# Load pre-trained model
model = Model(
    model_data='s3://manufacturing-models/failure-prediction/model.tar.gz',
    image_uri='your-ecr-repo/failure-predictor:latest',
    role=role,
    sagemaker_session=sagemaker_session
)

# Deploy endpoint
predictor = model.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large',
    endpoint_name='failure-prediction-endpoint'
)
```

### 3.2 Test Endpoint

```python
# test_endpoint.py
import boto3
import json

runtime = boto3.client('sagemaker-runtime')

response = runtime.invoke_endpoint(
    EndpointName='failure-prediction-endpoint',
    ContentType='application/json',
    Body=json.dumps({
        'equipment_id': 'EQ-001',
        'temperature': 75.5,
        'vibration': 2.3,
        'pressure': 10.2,
        'power_consumption': 15.8
    })
)

print(response['Body'].read())
```

## Step 4: Implement Maintenance Logic

### 4.1 Core Maintenance Function

```python
# predictive_maintenance.py
import boto3
import json
from typing import Dict, Any
from datetime import datetime, timedelta

class PredictiveMaintenanceSystem:
    def __init__(self):
        self.lookout = boto3.client('lookoutequipment')
        self.sagemaker = boto3.client('sagemaker-runtime')
        self.bedrock = boto3.client('bedrock-runtime')
        self.timestream = boto3.client('timestream-query')
        self.dynamodb = boto3.resource('dynamodb')
        self.eventbridge = boto3.client('events')
        
        self.maintenance_table = self.dynamodb.Table('manufacturing-maintenance')
        self.health_table = self.dynamodb.Table('manufacturing-equipment-health')
    
    def analyze_equipment_health(self, equipment_id: str) -> Dict[str, Any]:
        """Comprehensive equipment health analysis"""
        
        # Get recent sensor data from Timestream
        sensor_data = self.get_sensor_data(equipment_id, hours=24)
        
        # Check for anomalies with Lookout
        anomalies = self.check_anomalies(equipment_id, sensor_data)
        
        # Get failure prediction from SageMaker
        failure_prediction = self.get_failure_prediction(equipment_id, sensor_data)
        
        # Generate AI insights
        ai_insights = self.generate_maintenance_insights(
            equipment_id, sensor_data, anomalies, failure_prediction
        )
        
        # Store health record
        self.store_health_record(equipment_id, sensor_data, failure_prediction)
        
        # Create maintenance recommendations
        recommendations = self.create_maintenance_recommendations(
            equipment_id, failure_prediction, ai_insights
        )
        
        return {
            'equipment_id': equipment_id,
            'health_score': failure_prediction['health_score'],
            'failure_probability': failure_prediction['failure_probability'],
            'predicted_failure_time': failure_prediction.get('predicted_failure_time'),
            'anomalies_detected': len(anomalies),
            'insights': ai_insights,
            'recommendations': recommendations,
            'maintenance_urgency': self.calculate_urgency(failure_prediction)
        }
    
    def check_anomalies(self, equipment_id: str, sensor_data: Dict) -> list:
        """Check for anomalies using Lookout for Equipment"""
        
        # Prepare data for Lookout
        lookout_data = self.prepare_lookout_data(sensor_data)
        
        # Run anomaly detection
        response = self.lookout.list_inference_schedulers(
            DatasetName='manufacturing-equipment'
        )
        
        if response['InferenceSchedulers']:
            scheduler_name = response['InferenceSchedulers'][0]['InferenceSchedulerName']
            anomalies = self.lookout.describe_inference_scheduler(
                InferenceSchedulerName=scheduler_name
            )
            return anomalies.get('Anomalies', [])
        
        return []
    
    def get_failure_prediction(self, equipment_id: str, sensor_data: Dict) -> Dict:
        """Get failure prediction from SageMaker model"""
        
        payload = {
            'equipment_id': equipment_id,
            'sensor_data': sensor_data,
            'features': self.extract_features(sensor_data)
        }
        
        response = self.sagemaker.invoke_endpoint(
            EndpointName='failure-prediction-endpoint',
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        
        result = json.loads(response['Body'].read())
        return {
            'health_score': result.get('health_score', 0.0),
            'failure_probability': result.get('failure_probability', 0.0),
            'predicted_failure_time': result.get('predicted_failure_time'),
            'critical_components': result.get('critical_components', [])
        }
    
    def generate_maintenance_insights(self, equipment_id: str, 
                                    sensor_data: Dict, 
                                    anomalies: list,
                                    prediction: Dict) -> Dict:
        """Generate AI-powered maintenance insights"""
        
        prompt = f"""
        Analyze this manufacturing equipment data and provide maintenance insights:
        
        Equipment: {equipment_id}
        Health Score: {prediction['health_score']}
        Failure Probability: {prediction['failure_probability']}
        Anomalies Detected: {len(anomalies)}
        
        Sensor Data:
        - Temperature: {sensor_data.get('temperature', 'N/A')}°C
        - Vibration: {sensor_data.get('vibration', 'N/A')} mm/s
        - Pressure: {sensor_data.get('pressure', 'N/A')} bar
        - Power: {sensor_data.get('power', 'N/A')} kW
        
        Provide:
        1. Key performance indicators and trends
        2. Potential failure modes and causes
        3. Maintenance priority recommendations
        4. Operational optimization suggestions
        5. Risk assessment and mitigation strategies
        
        Format as structured JSON.
        """
        
        response = self.bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1500,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        return json.loads(result['content'][0]['text'])
    
    def create_maintenance_work_order(self, equipment_id: str, 
                                    maintenance_type: str, 
                                    urgency: str) -> Dict[str, Any]:
        """Generate AI-powered maintenance work orders"""
        
        # Get equipment specifications
        equipment_specs = self.get_equipment_specifications(equipment_id)
        
        # Generate maintenance procedures with Bedrock
        procedures = self.generate_maintenance_procedures(
            equipment_id, maintenance_type, equipment_specs
        )
        
        work_order = {
            'work_order_id': f"WO_{equipment_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            'equipment_id': equipment_id,
            'maintenance_type': maintenance_type,
            'urgency': urgency,
            'procedures': procedures,
            'created_at': datetime.utcnow().isoformat()
        }
        
        # Store work order
        self.maintenance_table.put_item(Item=work_order)
        
        # Send alert
        self.send_maintenance_alert(work_order)
        
        return work_order
    
    def send_maintenance_alert(self, work_order: Dict):
        """Send maintenance alert via EventBridge"""
        
        self.eventbridge.put_events(
            Entries=[{
                'Source': 'manufacturing.maintenance',
                'DetailType': 'Maintenance Required',
                'Detail': json.dumps({
                    'work_order_id': work_order['work_order_id'],
                    'equipment_id': work_order['equipment_id'],
                    'urgency': work_order['urgency'],
                    'maintenance_type': work_order['maintenance_type']
                })
            }]
        )
```

## Step 5: Testing

### 5.1 Test Maintenance System

```python
# test_maintenance.py
from predictive_maintenance import PredictiveMaintenanceSystem

system = PredictiveMaintenanceSystem()

# Test equipment health analysis
health = system.analyze_equipment_health('EQ-001')
print(json.dumps(health, indent=2))

# Test work order creation
work_order = system.create_maintenance_work_order(
    equipment_id='EQ-001',
    maintenance_type='preventive',
    urgency='high'
)
print(json.dumps(work_order, indent=2))
```

## Best Practices

1. **Data Quality**: Ensure clean, consistent sensor data
2. **Model Retraining**: Retrain models regularly with new data
3. **Alert Thresholds**: Set appropriate thresholds for maintenance alerts
4. **Monitoring**: Track maintenance prediction accuracy
5. **Documentation**: Maintain detailed maintenance records

## Troubleshooting

### High False Positive Rate

- Review sensor data quality
- Adjust anomaly detection thresholds
- Retrain failure prediction models
- Improve feature engineering

### Low Prediction Accuracy

- Increase training data volume
- Improve feature selection
- Tune model hyperparameters
- Review equipment specifications

## Next Steps

- Implement real-time monitoring dashboard
- Integrate with CMMS (Computerized Maintenance Management System)
- Add spare parts inventory optimization
- Deploy to production

---

**For more details, see the [Workshop Module 2](../workshop/module-2-predictive-maintenance.md)**

