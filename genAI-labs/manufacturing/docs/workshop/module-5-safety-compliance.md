# Module 5: Safety & Compliance

## Learning Objectives

By the end of this module, you will be able to:

- Integrate safety cameras with Rekognition
- Detect safety violations in real-time
- Analyze compliance documents with Comprehend
- Generate automated safety reports
- Set up compliance tracking systems
- Implement incident reporting automation

## Prerequisites

- Completed Module 4: Process Optimization
- Access to Amazon Rekognition
- Access to Amazon Comprehend
- Safety camera feeds (or sample video)
- Compliance documents for testing

## Duration

**Estimated Time**: 90 minutes

## Step 1: Set Up Safety Camera Integration

### 1.1 Configure Rekognition for Safety Detection

```bash
# Create Rekognition collection for safety monitoring
aws rekognition create-collection \
  --collection-id manufacturing-safety \
  --region us-east-1
```

### 1.2 Set Up Video Stream Processing

```python
# setup_video_processing.py
import boto3

kinesis_video = boto3.client('kinesisvideo')

# Create Kinesis Video Stream
response = kinesis_video.create_stream(
    StreamName='manufacturing-safety-cameras',
    DataRetentionInHours=24
)

print(f"Stream ARN: {response['StreamARN']}")
```

## Step 2: Create Safety Monitoring Lambda

### 2.1 Implement Safety Detection Function

```python
# backend/lambda/safety-monitoring/lambda_function.py
import json
import boto3
from datetime import datetime

rekognition = boto3.client('rekognition')
comprehend = boto3.client('comprehend')
bedrock = boto3.client('bedrock-runtime')
dynamodb = boto3.resource('dynamodb')
eventbridge = boto3.client('events')

def handler(event, context):
    """Monitor workplace safety and detect violations"""
    
    camera_feed = event.get('camera_feed')
    safety_rules = event.get('safety_rules', {})
    
    # Detect safety violations
    violations = detect_safety_violations(camera_feed, safety_rules)
    
    # Analyze safety patterns
    safety_patterns = analyze_safety_patterns(violations)
    
    # Generate safety recommendations
    recommendations = generate_safety_recommendations(
        violations, safety_patterns, safety_rules
    )
    
    # Store safety data
    store_safety_data(violations, recommendations)
    
    # Send alerts for critical violations
    if violations.get('critical_count', 0) > 0:
        send_safety_alert(violations, recommendations)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'violations': violations,
            'safety_score': calculate_safety_score(violations),
            'recommendations': recommendations
        })
    }

def detect_safety_violations(camera_feed, safety_rules):
    """Detect safety violations using Rekognition"""
    violations = []
    
    # Analyze video frame
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': 'manufacturing-dev-images', 'Name': camera_feed}},
        MaxLabels=20,
        MinConfidence=70
    )
    
    # Check for PPE violations
    ppe_violations = check_ppe_compliance(response['Labels'], safety_rules)
    violations.extend(ppe_violations)
    
    # Check for unsafe behaviors
    behavior_violations = check_unsafe_behaviors(response['Labels'], safety_rules)
    violations.extend(behavior_violations)
    
    return {
        'violations': violations,
        'critical_count': len([v for v in violations if v.get('severity') == 'critical']),
        'timestamp': datetime.utcnow().isoformat()
    }

def check_ppe_compliance(labels, safety_rules):
    """Check Personal Protective Equipment compliance"""
    violations = []
    required_ppe = safety_rules.get('required_ppe', [])
    
    detected_items = [label['Name'].lower() for label in labels]
    
    for ppe_item in required_ppe:
        if ppe_item.lower() not in detected_items:
            violations.append({
                'type': 'PPE_MISSING',
                'item': ppe_item,
                'severity': 'high',
                'description': f'Missing required PPE: {ppe_item}'
            })
    
    return violations

def generate_safety_recommendations(violations, patterns, rules):
    """Generate AI-powered safety recommendations"""
    prompt = f"""
    Analyze these workplace safety violations and provide recommendations:
    
    Violations Detected: {len(violations)}
    Critical Violations: {len([v for v in violations if v.get('severity') == 'critical'])}
    Safety Patterns: {patterns}
    
    Provide:
    1. Immediate actions required
    2. Long-term safety improvements
    3. Training recommendations
    4. Compliance status
    """
    
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 1500,
            'messages': [{'role': 'user', 'content': prompt}]
        })
    )
    
    result = json.loads(response['body'].read())
    return json.loads(result['content'][0]['text'])
```

## Step 3: Set Up Compliance Document Analysis

### 3.1 Configure Comprehend for Document Analysis

```python
# analyze_compliance_docs.py
import boto3

comprehend = boto3.client('comprehend')
textract = boto3.client('textract')

def analyze_compliance_document(document_s3_path):
    """Analyze compliance document using Comprehend and Textract"""
    
    # Extract text from document
    textract_response = textract.detect_document_text(
        Document={'S3Object': {'Bucket': 'manufacturing-dev-documents', 'Name': document_s3_path}}
    )
    
    # Extract text
    document_text = extract_text_from_textract(textract_response)
    
    # Analyze with Comprehend
    entities = comprehend.detect_entities(
        Text=document_text,
        LanguageCode='en'
    )
    
    # Extract compliance requirements
    compliance_requirements = extract_compliance_requirements(entities, document_text)
    
    return {
        'document': document_s3_path,
        'requirements': compliance_requirements,
        'compliance_status': check_compliance_status(compliance_requirements)
    }
```

## Step 4: Create Compliance Tracking System

### 4.1 Set Up Compliance Database

```bash
# Create compliance tracking table
aws dynamodb create-table \
  --table-name manufacturing-compliance \
  --attribute-definitions \
    AttributeName=requirement_id,AttributeType=S \
    AttributeName=timestamp,AttributeType=N \
  --key-schema \
    AttributeName=requirement_id,KeyType=HASH \
    AttributeName=timestamp,KeyType=RANGE \
  --billing-mode PAY_PER_REQUEST
```

### 4.2 Implement Compliance Monitoring

```python
# compliance_monitoring.py
def monitor_compliance(requirements, process_data):
    """Monitor compliance with regulatory requirements"""
    
    compliance_results = {}
    
    for requirement in requirements:
        compliance_status = check_requirement_compliance(
            requirement, process_data
        )
        
        compliance_results[requirement['id']] = {
            'requirement': requirement['name'],
            'compliant': compliance_status['compliant'],
            'evidence': compliance_status['evidence'],
            'last_checked': datetime.utcnow().isoformat()
        }
    
    # Generate compliance report
    report = generate_compliance_report(compliance_results)
    
    return {
        'overall_compliance': all(r['compliant'] for r in compliance_results.values()),
        'requirements': compliance_results,
        'report': report
    }
```

## Step 5: Set Up Incident Reporting

### 5.1 Create Incident Reporting System

```python
# incident_reporting.py
def create_incident_report(incident_data):
    """Create automated incident report"""
    
    # Generate report with Bedrock
    report = generate_incident_report(incident_data)
    
    # Store incident
    store_incident(incident_data, report)
    
    # Notify relevant parties
    notify_incident(incident_data, report)
    
    return report

def generate_incident_report(incident_data):
    """Generate AI-powered incident report"""
    prompt = f"""
    Create a comprehensive incident report:
    
    Incident Type: {incident_data.get('type')}
    Location: {incident_data.get('location')}
    Time: {incident_data.get('timestamp')}
    Description: {incident_data.get('description')}
    
    Provide:
    1. Incident summary
    2. Root cause analysis
    3. Immediate actions taken
    4. Preventive measures
    5. Follow-up recommendations
    """
    
    response = bedrock.invoke_model(
        modelId='anthropic.claude-3-5-sonnet-20241022-v2:0',
        body=json.dumps({
            'anthropic_version': 'bedrock-2023-05-31',
            'max_tokens': 2000,
            'messages': [{'role': 'user', 'content': prompt}]
        })
    )
    
    result = json.loads(response['body'].read())
    return json.loads(result['content'][0]['text'])
```

## Step 6: Testing

### 6.1 Test Safety Monitoring

```python
# test_safety.py
import boto3
import json

lambda_client = boto3.client('lambda')

# Test safety monitoring
response = lambda_client.invoke(
    FunctionName='manufacturing-safety-monitoring',
    Payload=json.dumps({
        'camera_feed': 's3://manufacturing-dev-images/safety-camera-001.jpg',
        'safety_rules': {
            'required_ppe': ['hard_hat', 'safety_vest', 'safety_glasses'],
            'prohibited_behaviors': ['running', 'improper_lifting']
        }
    })
)

result = json.loads(response['Payload'].read())
print(json.dumps(result, indent=2))
```

## Troubleshooting

### Issue: Rekognition Not Detecting PPE

**Solution**:
1. Improve image quality
2. Train custom labels model
3. Adjust detection confidence thresholds

### Issue: Compliance Documents Not Parsing Correctly

**Solution**:
1. Verify document format
2. Check Textract permissions
3. Improve document preprocessing

## Validation Checklist

Before proceeding to Module 6, verify:

- [ ] Safety monitoring system operational
- [ ] Compliance tracking working
- [ ] Incident reporting automated
- [ ] Safety alerts configured
- [ ] Compliance reports generating
- [ ] Test scenarios passing

## Next Steps

Congratulations! You've completed Module 5. You're now ready to:

1. **Proceed to Module 6**: [Production Deployment](./module-6-deployment.md)
2. **Explore Advanced Features**: Custom safety models
3. **Review Architecture**: Read the [Architecture Guide](../../architecture.md)

---

**Ready for Module 6? Let's deploy to production! 🚀**

