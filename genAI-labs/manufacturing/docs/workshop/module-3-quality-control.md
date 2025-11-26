# Module 3: Quality Control

## Learning Objectives

By the end of this module, you will be able to:

- Integrate Amazon Rekognition for visual inspection
- Deploy custom SageMaker vision models for defect detection
- Process image streams with Kinesis
- Implement real-time quality scoring
- Generate automated quality reports with Bedrock
- Set up quality feedback loops

## Prerequisites

- Completed Module 2: Predictive Maintenance
- Kinesis stream configured
- Access to Amazon Rekognition
- Access to Amazon SageMaker
- Sample product images for testing

## Duration

**Estimated Time**: 90 minutes

## Step 1: Set Up Image Processing Pipeline

### 1.1 Configure Kinesis Stream for Images

```bash
# Verify Kinesis stream exists
aws kinesis describe-stream --stream-name manufacturing-images

# If needed, create stream
aws kinesis create-stream \
  --stream-name manufacturing-images \
  --shard-count 5 \
  --region us-east-1
```

### 1.2 Create S3 Bucket for Images

```bash
# Create bucket for quality images
aws s3 mb s3://manufacturing-dev-quality-images \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket manufacturing-dev-quality-images \
  --versioning-configuration Status=Enabled
```

## Step 2: Configure Amazon Rekognition

### 2.1 Create Custom Labels Project

```bash
# Create Rekognition project
aws rekognition create-project \
  --project-name manufacturing-quality-control \
  --region us-east-1

# Create project version (requires training)
aws rekognition create-project-version \
  --project-arn arn:aws:rekognition:us-east-1:ACCOUNT_ID:project/manufacturing-quality-control/1234567890123 \
  --version-name v1 \
  --output-config S3Bucket=manufacturing-dev-data-lake,S3KeyPrefix=rekognition-output/ \
  --training-data-config file://config/rekognition-training-config.json \
  --testing-data-config file://config/rekognition-testing-config.json
```

### 2.2 Test Rekognition

```python
# test_rekognition.py
import boto3

rekognition = boto3.client('rekognition')

# Test image detection
with open('data/sample/product-image.jpg', 'rb') as image:
    response = rekognition.detect_labels(
        Image={'Bytes': image.read()},
        MaxLabels=10,
        MinConfidence=70
    )
    
    print(json.dumps(response, indent=2))
```

## Step 3: Deploy Custom Vision Model

### 3.1 Train Custom Defect Detection Model

```python
# train_defect_model.py
import boto3
import sagemaker
from sagemaker.pytorch import PyTorch

sagemaker_session = sagemaker.Session()
role = 'arn:aws:iam::ACCOUNT_ID:role/SageMakerExecutionRole'

# Create estimator
estimator = PyTorch(
    entry_point='defect_detection.py',
    role=role,
    instance_type='ml.p3.2xlarge',
    framework_version='2.0',
    py_version='py310',
    sagemaker_session=sagemaker_session
)

# Train model
estimator.fit({
    'training': 's3://manufacturing-dev-data-lake/defect-training/',
    'validation': 's3://manufacturing-dev-data-lake/defect-validation/'
})

# Deploy endpoint
predictor = estimator.deploy(
    initial_instance_count=1,
    instance_type='ml.m5.large',
    endpoint_name='defect-detection-endpoint'
)
```

## Step 4: Create Quality Control Lambda

### 4.1 Implement Quality Inspection Function

```python
# backend/lambda/quality-control/lambda_function.py
import json
import boto3
from datetime import datetime

rekognition = boto3.client('rekognition')
sagemaker = boto3.client('sagemaker-runtime')
bedrock = boto3.client('bedrock-runtime')
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

def handler(event, context):
    """Process product images for quality inspection"""
    
    # Get image from Kinesis event
    image_data = get_image_from_event(event)
    product_id = event['product_id']
    product_specs = event.get('product_specs', {})
    
    # Perform visual inspection
    visual_inspection = perform_visual_inspection(image_data, product_specs)
    
    # Detect defects
    defect_analysis = detect_defects(image_data, product_specs)
    
    # Analyze dimensions
    dimensional_analysis = analyze_dimensions(image_data, product_specs)
    
    # Generate quality report
    quality_report = generate_quality_report(
        product_id, visual_inspection, defect_analysis, dimensional_analysis
    )
    
    # Store results
    store_quality_results(product_id, quality_report, image_data)
    
    return {
        'statusCode': 200,
        'body': json.dumps(quality_report)
    }

def perform_visual_inspection(image_data, product_specs):
    """Use Rekognition for general visual inspection"""
    response = rekognition.detect_labels(
        Image={'Bytes': image_data},
        MaxLabels=20,
        MinConfidence=70
    )
    
    return {
        'labels': response['Labels'],
        'overall_quality': calculate_quality_score(response['Labels'])
    }

def detect_defects(image_data, product_specs):
    """Use custom SageMaker model for defect detection"""
    payload = {
        'image': base64.b64encode(image_data).decode('utf-8'),
        'product_type': product_specs.get('product_type')
    }
    
    response = sagemaker.invoke_endpoint(
        EndpointName='defect-detection-endpoint',
        ContentType='application/json',
        Body=json.dumps(payload)
    )
    
    result = json.loads(response['Body'].read())
    return {
        'defects_detected': result.get('defects', []),
        'defect_count': len(result.get('defects', [])),
        'severity': result.get('severity', 'low')
    }

def generate_quality_report(product_id, visual, defects, dimensions):
    """Generate AI-powered quality report"""
    prompt = f"""
    Generate a quality inspection report:
    
    Product ID: {product_id}
    Visual Quality: {visual['overall_quality']}
    Defects Found: {defects['defect_count']}
    Defect Severity: {defects['severity']}
    
    Provide:
    1. Overall quality score (0-100)
    2. Pass/Fail recommendation
    3. Key quality indicators
    4. Improvement recommendations
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
```

## Step 5: Set Up Quality Feedback Loop

### 5.1 Create Quality Metrics Table

```bash
# Create quality metrics table
aws dynamodb create-table \
  --table-name manufacturing-quality-metrics \
  --attribute-definitions \
    AttributeName=product_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=product_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
```

### 5.2 Implement Feedback System

```python
# quality_feedback.py
def update_quality_thresholds(quality_results):
    """Update quality thresholds based on results"""
    
    # Analyze quality trends
    trends = analyze_quality_trends(quality_results)
    
    # Adjust thresholds if needed
    if trends['defect_rate'] > 0.05:  # 5% defect rate
        adjust_inspection_parameters(trends)
        send_alert_to_production_team(trends)
```

## Step 6: Testing

### 6.1 Test Quality Inspection

```python
# test_quality.py
import boto3
import json

lambda_client = boto3.client('lambda')

# Read test image
with open('data/sample/product-image.jpg', 'rb') as f:
    image_data = f.read()

# Test quality inspection
response = lambda_client.invoke(
    FunctionName='manufacturing-quality-control',
    Payload=json.dumps({
        'product_id': 'PROD-001',
        'image_data': base64.b64encode(image_data).decode('utf-8'),
        'product_specs': {
            'product_type': 'widget',
            'expected_dimensions': {'width': 10, 'height': 10, 'depth': 5}
        }
    })
)

result = json.loads(response['Payload'].read())
print(json.dumps(result, indent=2))
```

## Troubleshooting

### Issue: Rekognition Detection Accuracy Low

**Solution**:
1. Improve image quality
2. Train custom labels model
3. Adjust confidence thresholds

### Issue: SageMaker Vision Model Slow

**Solution**:
1. Optimize model architecture
2. Use GPU instances for inference
3. Implement caching for similar products

## Validation Checklist

Before proceeding to Module 4, verify:

- [ ] Rekognition configured and working
- [ ] Custom vision model deployed
- [ ] Quality Lambda function processing images
- [ ] Quality reports being generated
- [ ] Feedback loop operational
- [ ] Test inspections passing

## Next Steps

Congratulations! You've completed Module 3. You're now ready to:

1. **Proceed to Module 4**: [Process Optimization](./module-4-process-optimization.md)
2. **Explore Advanced Features**: Custom defect detection models
3. **Review Architecture**: Read the [Architecture Guide](../../architecture.md)

---

**Ready for Module 4? Let's optimize manufacturing processes! 🚀**

