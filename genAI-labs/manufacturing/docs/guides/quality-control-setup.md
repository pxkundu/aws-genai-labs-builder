# Quality Control Setup Guide

## Overview

This guide provides detailed instructions for setting up and configuring the AI-powered quality control system for manufacturing. The system combines Amazon Rekognition, custom SageMaker vision models, and Amazon Bedrock to deliver real-time visual inspection and defect detection.

## Architecture

The quality control system consists of:

1. **Image Ingestion**: Kinesis streams for product images
2. **Visual Inspection**: Rekognition for general object detection
3. **Defect Detection**: Custom SageMaker vision models
4. **Quality Analysis**: Bedrock for quality report generation
5. **Storage**: S3 for images, DynamoDB for results
6. **Feedback Loop**: Quality metrics and threshold adjustment

## Prerequisites

- AWS Account with required services enabled
- Bedrock model access configured
- Rekognition access
- SageMaker endpoint deployed (or use pre-built models)
- Kinesis stream configured
- S3 buckets created

## Step 1: Deploy Infrastructure

### 1.1 Create Kinesis Stream for Images

```bash
# Create Kinesis stream for images
aws kinesis create-stream \
  --stream-name manufacturing-images \
  --shard-count 5 \
  --region us-east-1

# Verify stream creation
aws kinesis describe-stream \
  --stream-name manufacturing-images
```

### 1.2 Create S3 Buckets

```bash
# Create bucket for quality images
aws s3 mb s3://manufacturing-quality-images \
  --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket manufacturing-quality-images \
  --versioning-configuration Status=Enabled

# Create bucket for defect training data
aws s3 mb s3://manufacturing-defect-training \
  --region us-east-1
```

### 1.3 Create DynamoDB Tables

```bash
# Quality results table
aws dynamodb create-table \
  --table-name manufacturing-quality-results \
  --attribute-definitions \
    AttributeName=product_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=product_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST

# Quality metrics table
aws dynamodb create-table \
  --table-name manufacturing-quality-metrics \
  --attribute-definitions \
    AttributeName=metric_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=metric_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
```

## Step 2: Configure Rekognition

### 2.1 Create Custom Labels Project

```bash
# Create Rekognition project
aws rekognition create-project \
  --project-name manufacturing-quality-control \
  --region us-east-1

# Get project ARN
PROJECT_ARN=$(aws rekognition list-projects \
  --query 'ProjectDescriptions[0].ProjectArn' \
  --output text)

echo "Project ARN: $PROJECT_ARN"
```

### 2.2 Upload Training Data

```bash
# Upload training images
aws s3 sync data/training/defect-images/ \
  s3://manufacturing-defect-training/training/

# Upload validation images
aws s3 sync data/validation/defect-images/ \
  s3://manufacturing-defect-training/validation/
```

## Step 3: Deploy Custom Vision Model

### 3.1 Train Defect Detection Model

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
    instance_type='ml.p3.2xlarge',  # GPU instance for training
    framework_version='2.0',
    py_version='py310',
    sagemaker_session=sagemaker_session,
    hyperparameters={
        'epochs': 50,
        'batch-size': 32,
        'learning-rate': 0.001
    }
)

# Train model
estimator.fit({
    'training': 's3://manufacturing-defect-training/training/',
    'validation': 's3://manufacturing-defect-training/validation/'
})

# Deploy endpoint
predictor = estimator.deploy(
    initial_instance_count=1,
    instance_type='ml.g4dn.xlarge',  # GPU for inference
    endpoint_name='defect-detection-endpoint'
)
```

## Step 4: Implement Quality Control Logic

### 4.1 Core Quality Control Function

```python
# quality_control.py
import boto3
import json
import base64
from typing import Dict, Any
from datetime import datetime

class QualityControlSystem:
    def __init__(self):
        self.rekognition = boto3.client('rekognition')
        self.sagemaker = boto3.client('sagemaker-runtime')
        self.bedrock = boto3.client('bedrock-runtime')
        self.s3 = boto3.client('s3')
        self.dynamodb = boto3.resource('dynamodb')
        
        self.quality_results_table = self.dynamodb.Table('manufacturing-quality-results')
        self.quality_metrics_table = self.dynamodb.Table('manufacturing-quality-metrics')
    
    def inspect_product(self, product_id: str, image_data: bytes, 
                       product_specs: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive product quality inspection"""
        
        # Visual inspection using Rekognition
        visual_inspection = self.perform_visual_inspection(image_data, product_specs)
        
        # Defect detection using custom model
        defect_analysis = self.detect_defects(image_data, product_specs)
        
        # Dimensional analysis
        dimensional_analysis = self.analyze_dimensions(image_data, product_specs)
        
        # Surface quality assessment
        surface_quality = self.assess_surface_quality(image_data, product_specs)
        
        # Generate quality report
        quality_report = self.generate_quality_report(
            product_id, visual_inspection, defect_analysis, 
            dimensional_analysis, surface_quality
        )
        
        # Store results
        self.store_quality_results(product_id, quality_report, image_data)
        
        # Update quality metrics
        self.update_quality_metrics(product_id, quality_report)
        
        return quality_report
    
    def perform_visual_inspection(self, image_data: bytes, 
                                 product_specs: Dict) -> Dict:
        """Use Rekognition for general visual inspection"""
        
        response = self.rekognition.detect_labels(
            Image={'Bytes': image_data},
            MaxLabels=20,
            MinConfidence=70
        )
        
        # Check for expected product features
        expected_features = product_specs.get('expected_features', [])
        detected_features = [label['Name'] for label in response['Labels']]
        
        feature_compliance = all(
            feature in detected_features for feature in expected_features
        )
        
        return {
            'labels': response['Labels'],
            'feature_compliance': feature_compliance,
            'overall_quality': self.calculate_visual_quality(response['Labels'])
        }
    
    def detect_defects(self, image_data: bytes, product_specs: Dict) -> Dict:
        """Use custom SageMaker model for defect detection"""
        
        payload = {
            'image': base64.b64encode(image_data).decode('utf-8'),
            'product_type': product_specs.get('product_type'),
            'expected_quality': product_specs.get('quality_standard', 'high')
        }
        
        response = self.sagemaker.invoke_endpoint(
            EndpointName='defect-detection-endpoint',
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        
        result = json.loads(response['Body'].read())
        
        return {
            'defects_detected': result.get('defects', []),
            'defect_count': len(result.get('defects', [])),
            'defect_severity': result.get('severity', 'low'),
            'defect_locations': result.get('locations', []),
            'confidence_scores': result.get('confidence', [])
        }
    
    def generate_quality_report(self, product_id: str, visual: Dict, 
                              defects: Dict, dimensions: Dict, 
                              surface: Dict) -> Dict:
        """Generate AI-powered quality report"""
        
        prompt = f"""
        Generate a comprehensive quality inspection report:
        
        Product ID: {product_id}
        Visual Quality Score: {visual.get('overall_quality', 0)}
        Defects Detected: {defects.get('defect_count', 0)}
        Defect Severity: {defects.get('defect_severity', 'none')}
        Dimensional Accuracy: {dimensions.get('accuracy', 0)}
        Surface Quality: {surface.get('quality_score', 0)}
        
        Provide:
        1. Overall quality score (0-100)
        2. Pass/Fail recommendation with reasoning
        3. Key quality indicators
        4. Specific defect details if any
        5. Improvement recommendations
        6. Compliance status
        
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
        report = json.loads(result['content'][0]['text'])
        
        # Add calculated metrics
        report['overall_quality_score'] = self.calculate_overall_quality(
            visual, defects, dimensions, surface
        )
        report['pass_fail_status'] = self.determine_pass_fail(report)
        
        return report
    
    def calculate_overall_quality(self, visual: Dict, defects: Dict, 
                                 dimensions: Dict, surface: Dict) -> float:
        """Calculate overall quality score"""
        
        visual_score = visual.get('overall_quality', 0) * 0.3
        defect_penalty = defects.get('defect_count', 0) * 5
        dimension_score = dimensions.get('accuracy', 0) * 0.3
        surface_score = surface.get('quality_score', 0) * 0.4
        
        overall = visual_score + dimension_score + surface_score - defect_penalty
        return max(0, min(100, overall))
    
    def store_quality_results(self, product_id: str, report: Dict, 
                            image_data: bytes):
        """Store quality inspection results"""
        
        # Upload image to S3
        image_key = f"quality-inspections/{product_id}/{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        self.s3.put_object(
            Bucket='manufacturing-quality-images',
            Key=image_key,
            Body=image_data,
            ContentType='image/jpeg'
        )
        
        # Store results in DynamoDB
        self.quality_results_table.put_item(
            Item={
                'product_id': product_id,
                'timestamp': int(datetime.utcnow().timestamp()),
                'quality_score': report['overall_quality_score'],
                'pass_fail': report['pass_fail_status'],
                'defects': report.get('defects', []),
                'image_s3_key': image_key,
                'report': report,
                'created_at': datetime.utcnow().isoformat()
            }
        )
```

## Step 5: Testing

### 5.1 Test Quality Control

```python
# test_quality_control.py
from quality_control import QualityControlSystem

system = QualityControlSystem()

# Test with sample image
with open('data/sample/product-image.jpg', 'rb') as f:
    image_data = f.read()

product_specs = {
    'product_type': 'widget',
    'expected_features': ['metal', 'smooth', 'rectangular'],
    'quality_standard': 'high',
    'dimensional_tolerance': 0.01
}

result = system.inspect_product(
    product_id='PROD-001',
    image_data=image_data,
    product_specs=product_specs
)

print(json.dumps(result, indent=2))
```

## Best Practices

1. **Image Quality**: Ensure high-quality images for accurate inspection
2. **Model Training**: Regularly retrain models with new defect patterns
3. **Threshold Tuning**: Adjust quality thresholds based on production data
4. **Feedback Loop**: Implement continuous improvement based on results
5. **Performance**: Optimize for sub-2 second inspection time

## Troubleshooting

### Low Detection Accuracy

- Improve image quality and lighting
- Retrain models with more diverse data
- Adjust confidence thresholds
- Use ensemble of multiple models

### High False Positive Rate

- Review defect detection logic
- Improve training data quality
- Adjust severity thresholds
- Implement human-in-the-loop validation

## Next Steps

- Implement real-time quality dashboard
- Integrate with production line systems
- Add multi-angle inspection
- Deploy to production

---

**For more details, see the [Workshop Module 3](../workshop/module-3-quality-control.md)**

