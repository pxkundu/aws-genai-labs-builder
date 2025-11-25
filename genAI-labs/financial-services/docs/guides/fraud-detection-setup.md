# Fraud Detection System Setup Guide

## Overview

This guide provides detailed instructions for setting up and configuring the real-time fraud detection system for financial services applications. The fraud detection system combines AWS Fraud Detector, Amazon SageMaker, and Amazon Bedrock to deliver sub-50ms fraud detection with high accuracy.

## Architecture

The fraud detection system consists of:

1. **Event Ingestion**: Kinesis Data Streams for real-time transaction events
2. **Primary Detection**: AWS Fraud Detector for initial fraud scoring
3. **Deep Analysis**: SageMaker ML models for complex pattern detection
4. **GenAI Enhancement**: Bedrock for detailed fraud analysis
5. **Alert System**: EventBridge for real-time alerts
6. **Storage**: DynamoDB for fraud events and patterns

## Prerequisites

- AWS Account with required services enabled
- Bedrock model access configured
- AWS Fraud Detector access
- SageMaker endpoint deployed (or use pre-built models)
- DynamoDB tables created
- Kinesis stream configured

## Step 1: Deploy Infrastructure

### 1.1 Create Kinesis Data Stream

```bash
# Create Kinesis stream for transactions
aws kinesis create-stream \
  --stream-name financial-transactions \
  --shard-count 5 \
  --region us-east-1

# Verify stream creation
aws kinesis describe-stream \
  --stream-name financial-transactions
```

### 1.2 Create DynamoDB Tables

```bash
# Fraud events table
aws dynamodb create-table \
  --table-name financial-fraud-events \
  --attribute-definitions \
    AttributeName=event_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=event_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST \
  --sse-specification Enabled=true,SSEType=KMS

# Fraud patterns table
aws dynamodb create-table \
  --table-name financial-fraud-patterns \
  --attribute-definitions \
    AttributeName=pattern_id,AttributeType=S \
  --key-schema \
    AttributeName=pattern_id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --sse-specification Enabled=true,SSEType=KMS
```

## Step 2: Set Up AWS Fraud Detector

### 2.1 Create Event Type

```bash
# Create event type for transactions
aws frauddetector create-event-type \
  --name transaction \
  --event-variables \
    Name=amount,DataType=FLOAT \
    Name=merchant,DataType=STRING \
    Name=location,DataType=STRING \
    Name=time_of_day,DataType=STRING \
    Name=device_id,DataType=STRING \
    Name=ip_address,DataType=IP_ADDRESS \
  --labels Name=legitimate,Value=0 Name=fraud,Value=1
```

### 2.2 Create Fraud Detector Model

```bash
# Create model
aws frauddetector create-model \
  --model-id transaction-fraud-detector \
  --event-type-name transaction \
  --model-type ONLINE_FRAUD_INSIGHTS

# Train model (requires training data)
aws frauddetector create-model-version \
  --model-id transaction-fraud-detector \
  --model-type ONLINE_FRAUD_INSIGHTS \
  --training-data-source s3://financial-services-data/training/fraud-data.csv
```

## Step 3: Deploy Lambda Functions

### 3.1 Create Fraud Detection Lambda

```bash
# Package Lambda function
cd backend/lambda/fraud-detection
zip -r fraud-detection.zip .

# Create Lambda function
aws lambda create-function \
  --function-name financial-fraud-detection \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_function.handler \
  --zip-file fileb://fraud-detection.zip \
  --timeout 30 \
  --memory-size 512 \
  --vpc-config SubnetIds=subnet-xxx,SecurityGroupIds=sg-xxx \
  --environment Variables={
    FRAUD_DETECTOR_ID=transaction-fraud-detector,
    SAGEMAKER_ENDPOINT=fraud-ml-endpoint,
    BEDROCK_MODEL_ID=anthropic.claude-3-5-sonnet-20241022-v2:0,
    KINESIS_STREAM=financial-transactions
  }
```

### 3.2 Create Event Processor Lambda

```bash
# Package event processor
cd backend/lambda/event-processor
zip -r event-processor.zip .

# Create Lambda function
aws lambda create-function \
  --function-name financial-event-processor \
  --runtime python3.11 \
  --role arn:aws:iam::ACCOUNT_ID:role/lambda-execution-role \
  --handler lambda_function.handler \
  --zip-file fileb://event-processor.zip \
  --timeout 60 \
  --memory-size 256
```

### 3.3 Configure Kinesis Trigger

```bash
# Add Kinesis event source mapping
aws lambda create-event-source-mapping \
  --function-name financial-event-processor \
  --event-source-arn arn:aws:kinesis:us-east-1:ACCOUNT_ID:stream/financial-transactions \
  --starting-position LATEST \
  --batch-size 100
```

## Step 4: Configure SageMaker Endpoint

### 4.1 Deploy Fraud Detection Model

```python
# deploy_fraud_model.py
import boto3
import sagemaker
from sagemaker.model import Model
from sagemaker.predictor import Predictor

sagemaker_session = sagemaker.Session()
role = 'arn:aws:iam::ACCOUNT_ID:role/SageMakerExecutionRole'

# Load pre-trained model
model = Model(
    model_data='s3://financial-services-models/fraud-detector/model.tar.gz',
    image_uri='your-ecr-repo/fraud-detector:latest',
    role=role,
    sagemaker_session=sagemaker_session
)

# Deploy endpoint
predictor = model.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large',
    endpoint_name='fraud-ml-endpoint'
)
```

### 4.2 Test Endpoint

```python
# test_endpoint.py
import boto3
import json

runtime = boto3.client('sagemaker-runtime')

response = runtime.invoke_endpoint(
    EndpointName='fraud-ml-endpoint',
    ContentType='application/json',
    Body=json.dumps({
        'transaction_id': 'test-001',
        'amount': 1000.00,
        'merchant': 'test-merchant',
        'location': 'US',
        'device_id': 'device-123'
    })
)

print(response['Body'].read())
```

## Step 5: Implement Fraud Detection Logic

### 5.1 Core Fraud Detection Function

```python
# fraud_detection.py
import boto3
import json
from typing import Dict, Any
from datetime import datetime

class FraudDetectionSystem:
    def __init__(self):
        self.fraud_detector = boto3.client('frauddetector')
        self.sagemaker = boto3.client('sagemaker-runtime')
        self.bedrock = boto3.client('bedrock-runtime')
        self.dynamodb = boto3.resource('dynamodb')
        self.eventbridge = boto3.client('events')
        
        self.fraud_events_table = self.dynamodb.Table('financial-fraud-events')
        self.fraud_patterns_table = self.dynamodb.Table('financial-fraud-patterns')
    
    def detect_fraud(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """Real-time fraud detection for transaction"""
        
        # Step 1: Get initial fraud score from Fraud Detector
        fraud_score = self.get_fraud_detector_score(transaction)
        
        # Step 2: If high risk, perform deep analysis
        if fraud_score > 0.7:
            ml_score = self.get_ml_score(transaction)
            enhanced_analysis = self.enhanced_fraud_analysis(
                transaction, fraud_score, ml_score
            )
            
            # Step 3: Store fraud event
            self.store_fraud_event(transaction, enhanced_analysis)
            
            # Step 4: Send alert
            self.send_fraud_alert(transaction, enhanced_analysis)
            
            return enhanced_analysis
        
        return {
            'fraud_score': fraud_score,
            'risk_level': 'low',
            'recommendation': 'approve',
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_fraud_detector_score(self, transaction: Dict) -> float:
        """Get fraud score from AWS Fraud Detector"""
        
        event_variables = {
            'amount': str(transaction['amount']),
            'merchant': transaction.get('merchant', 'unknown'),
            'location': transaction.get('location', 'unknown'),
            'time_of_day': transaction.get('time_of_day', 'unknown'),
            'device_id': transaction.get('device_id', 'unknown'),
            'ip_address': transaction.get('ip_address', '0.0.0.0')
        }
        
        response = self.fraud_detector.get_event_prediction(
            detectorId='transaction-fraud-detector',
            eventId=transaction['transaction_id'],
            eventTypeName='transaction',
            eventVariables=event_variables
        )
        
        # Extract fraud score
        model_scores = response.get('modelScores', [])
        if model_scores:
            return float(model_scores[0]['scores'].get('fraud', 0))
        
        return 0.0
    
    def get_ml_score(self, transaction: Dict) -> float:
        """Get fraud score from SageMaker ML model"""
        
        payload = {
            'transaction_id': transaction['transaction_id'],
            'amount': transaction['amount'],
            'merchant': transaction.get('merchant'),
            'location': transaction.get('location'),
            'customer_history': transaction.get('customer_history', {})
        }
        
        response = self.sagemaker.invoke_endpoint(
            EndpointName='fraud-ml-endpoint',
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        
        result = json.loads(response['Body'].read())
        return result.get('fraud_probability', 0.0)
    
    def enhanced_fraud_analysis(self, transaction: Dict, 
                                fraud_score: float, ml_score: float) -> Dict:
        """Enhanced fraud analysis using GenAI"""
        
        prompt = f"""
        Analyze this potentially fraudulent transaction:
        
        Transaction Details:
        - Transaction ID: {transaction['transaction_id']}
        - Amount: ${transaction['amount']}
        - Merchant: {transaction.get('merchant', 'unknown')}
        - Location: {transaction.get('location', 'unknown')}
        - Time: {transaction.get('timestamp', 'unknown')}
        - Customer ID: {transaction.get('customer_id', 'unknown')}
        
        Fraud Scores:
        - Fraud Detector Score: {fraud_score:.2f}
        - ML Model Score: {ml_score:.2f}
        
        Provide:
        1. Fraud likelihood (0-100%)
        2. Key risk indicators
        3. Recommended action (approve/decline/review)
        4. Explanation for decision
        5. Similar fraud patterns (if any)
        
        Format as JSON.
        """
        
        response = self.bedrock.invoke_model(
            modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
            body=json.dumps({
                'anthropic_version': 'bedrock-2023-05-31',
                'max_tokens': 1000,
                'messages': [{'role': 'user', 'content': prompt}]
            })
        )
        
        result = json.loads(response['body'].read())
        analysis = json.loads(result['content'][0]['text'])
        
        return {
            'fraud_score': max(fraud_score, ml_score),
            'risk_level': self.determine_risk_level(max(fraud_score, ml_score)),
            'recommendation': analysis.get('recommended_action', 'review'),
            'key_indicators': analysis.get('risk_indicators', []),
            'explanation': analysis.get('explanation', ''),
            'similar_patterns': analysis.get('similar_patterns', []),
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def determine_risk_level(self, score: float) -> str:
        """Determine risk level from score"""
        if score >= 0.8:
            return 'critical'
        elif score >= 0.6:
            return 'high'
        elif score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def store_fraud_event(self, transaction: Dict, analysis: Dict):
        """Store fraud event in DynamoDB"""
        
        self.fraud_events_table.put_item(
            Item={
                'event_id': transaction['transaction_id'],
                'timestamp': int(datetime.utcnow().timestamp()),
                'transaction': transaction,
                'analysis': analysis,
                'created_at': datetime.utcnow().isoformat()
            }
        )
    
    def send_fraud_alert(self, transaction: Dict, analysis: Dict):
        """Send fraud alert via EventBridge"""
        
        self.eventbridge.put_events(
            Entries=[{
                'Source': 'financial.fraud',
                'DetailType': 'Fraud Detected',
                'Detail': json.dumps({
                    'transaction_id': transaction['transaction_id'],
                    'fraud_score': analysis['fraud_score'],
                    'risk_level': analysis['risk_level'],
                    'recommendation': analysis['recommendation'],
                    'timestamp': analysis['timestamp']
                })
            }]
        )
```

## Step 6: Testing

### 6.1 Test Fraud Detection

```python
# test_fraud_detection.py
from fraud_detection import FraudDetectionSystem

system = FraudDetectionSystem()

# Test with suspicious transaction
suspicious_transaction = {
    'transaction_id': 'test-001',
    'amount': 10000.00,
    'merchant': 'overseas_atm',
    'location': 'different_country',
    'timestamp': '2024-01-01T03:00:00Z',
    'customer_id': 'customer-123',
    'device_id': 'new-device',
    'ip_address': '192.168.1.1'
}

result = system.detect_fraud(suspicious_transaction)
print(json.dumps(result, indent=2))
```

### 6.2 Load Testing

```bash
# Run load test
npm run load-test -- \
  --target https://api.example.com/fraud-detection \
  --duration 60 \
  --rate 1000
```

## Best Practices

1. **Low Latency**: Target < 50ms for fraud detection
2. **Accuracy**: Balance between fraud detection and false positives
3. **Monitoring**: Track fraud detection metrics continuously
4. **Model Updates**: Retrain models regularly with new fraud patterns
5. **Alerting**: Set up real-time alerts for high-risk transactions

## Troubleshooting

### High Latency

- Check Kinesis stream shard count
- Optimize Lambda function memory
- Review SageMaker endpoint configuration
- Enable caching for repeated patterns

### Low Detection Accuracy

- Review training data quality
- Retrain Fraud Detector model
- Tune ML model hyperparameters
- Improve feature engineering

## Next Steps

- Implement fraud pattern learning
- Add real-time dashboard
- Integrate with customer notification system
- Deploy to production

---

**For more details, see the [Workshop Module 2](../workshop/module-2-fraud-detection.md)**

