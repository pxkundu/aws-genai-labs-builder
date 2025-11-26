# Module 6: Production Deployment

## Learning Objectives

By the end of this module, you will be able to:

- Deploy infrastructure using Infrastructure as Code
- Set up CI/CD pipelines for manufacturing systems
- Configure comprehensive monitoring and alerting
- Implement security best practices
- Optimize performance for production workloads
- Ensure production readiness

## Prerequisites

- Completed all previous modules (1-5)
- Terraform or CDK installed
- GitHub Actions or similar CI/CD platform
- Production AWS account access

## Duration

**Estimated Time**: 60 minutes

## Step 1: Infrastructure as Code

### 1.1 Deploy with Terraform

```bash
# Navigate to infrastructure directory
cd infrastructure/terraform

# Initialize Terraform
terraform init

# Review deployment plan
terraform plan -out=production.tfplan

# Deploy to production
terraform apply production.tfplan

# Save outputs
terraform output -json > ../../config/production-outputs.json
```

### 1.2 Verify Infrastructure

```bash
# Verify all resources created
terraform state list

# Check specific resources
terraform state show aws_iot_thing_group.ManufacturingEquipment
terraform state show aws_timestreamwrite_database.manufacturing_sensors
```

## Step 2: Set Up CI/CD Pipeline

### 2.1 Create GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy Manufacturing AI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v2
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest
      
      - name: Run tests
        run: pytest tests/
      
      - name: Deploy Lambda functions
        run: ./scripts/deploy-lambdas.sh --environment production
      
      - name: Deploy infrastructure
        run: |
          cd infrastructure/terraform
          terraform init
          terraform apply -auto-approve
```

## Step 3: Configure Monitoring

### 3.1 Set Up CloudWatch Dashboards

```python
# setup_dashboards.py
import boto3

cloudwatch = boto3.client('cloudwatch')

# Create dashboard
dashboard_body = {
    'widgets': [
        {
            'type': 'metric',
            'properties': {
                'metrics': [
                    ['Manufacturing/Maintenance', 'EquipmentHealthScore'],
                    ['Manufacturing/Quality', 'QualityScore'],
                    ['Manufacturing/OEE', 'OEE_Score']
                ],
                'period': 300,
                'stat': 'Average',
                'region': 'us-east-1',
                'title': 'Manufacturing KPIs'
            }
        }
    ]
}

cloudwatch.put_dashboard(
    DashboardName='Manufacturing-Overview',
    DashboardBody=json.dumps(dashboard_body)
)
```

### 3.2 Set Up Alarms

```bash
# Create alarm for equipment health
aws cloudwatch put-metric-alarm \
  --alarm-name manufacturing-low-health \
  --alarm-description "Alert when equipment health is low" \
  --metric-name EquipmentHealthScore \
  --namespace Manufacturing/Maintenance \
  --statistic Average \
  --period 300 \
  --threshold 0.7 \
  --comparison-operator LessThanThreshold \
  --evaluation-periods 2

# Create alarm for high defect rate
aws cloudwatch put-metric-alarm \
  --alarm-name manufacturing-high-defects \
  --alarm-description "Alert when defect rate is high" \
  --metric-name DefectRate \
  --namespace Manufacturing/Quality \
  --statistic Average \
  --period 300 \
  --threshold 0.05 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2
```

## Step 4: Security Hardening

### 4.1 Review IAM Policies

```bash
# Review Lambda execution role
aws iam get-role-policy \
  --role-name ManufacturingLambdaRole \
  --policy-name ManufacturingLambdaPolicy

# Review IoT device policies
aws iot get-policy --policy-name ManufacturingDevicePolicy
```

### 4.2 Enable Encryption

```bash
# Enable encryption for DynamoDB tables
aws dynamodb update-table \
  --table-name manufacturing-equipment \
  --sse-specification Enabled=true,SSEType=KMS

# Enable encryption for S3 buckets
aws s3api put-bucket-encryption \
  --bucket manufacturing-dev-data-lake \
  --server-side-encryption-configuration '{
    "Rules": [{
      "ApplyServerSideEncryptionByDefault": {
        "SSEAlgorithm": "AES256"
      }
    }]
  }'
```

## Step 5: Performance Optimization

### 5.1 Optimize Lambda Functions

```bash
# Update Lambda memory and timeout
aws lambda update-function-configuration \
  --function-name manufacturing-predictive-maintenance \
  --memory-size 1024 \
  --timeout 120

# Enable provisioned concurrency for critical functions
aws lambda put-provisioned-concurrency-config \
  --function-name manufacturing-predictive-maintenance \
  --qualifier PROD \
  --provisioned-concurrent-executions 10
```

### 5.2 Optimize Kinesis Streams

```bash
# Update shard count for high throughput
aws kinesis update-shard-count \
  --stream-name manufacturing-images \
  --target-shard-count 10 \
  --scaling-type UNIFORM_SCALING
```

## Step 6: Production Readiness Checklist

### 6.1 Pre-Deployment Checklist

- [ ] All tests passing
- [ ] Security scan completed
- [ ] Performance testing completed
- [ ] Backup strategy configured
- [ ] Monitoring and alerting set up
- [ ] Disaster recovery plan documented
- [ ] Cost optimization reviewed
- [ ] Documentation updated
- [ ] Rollback plan prepared

### 6.2 Post-Deployment Validation

```bash
# Run smoke tests
./scripts/smoke-tests.sh --environment production

# Verify all services
./scripts/verify-deployment.sh

# Check metrics
aws cloudwatch get-metric-statistics \
  --namespace Manufacturing/Maintenance \
  --metric-name EquipmentHealthScore \
  --start-time $(date -u -d '1 hour ago' +%Y-%m-%dT%H:%M:%S) \
  --end-time $(date -u +%Y-%m-%dT%H:%M:%S) \
  --period 300 \
  --statistics Average
```

## Step 7: Documentation

### 7.1 Create Runbooks

```markdown
# runbooks/maintenance-alert.md
## Maintenance Alert Response

### Symptoms
- CloudWatch alarm: manufacturing-low-health
- Equipment health score below threshold

### Steps
1. Check equipment status in dashboard
2. Review recent sensor data
3. Generate maintenance work order
4. Assign technician
5. Monitor until resolved
```

## Troubleshooting

### Issue: Deployment Fails

**Solution**:
1. Check Terraform state
2. Verify IAM permissions
3. Review CloudWatch logs
4. Check resource limits

### Issue: High Latency in Production

**Solution**:
1. Enable Lambda provisioned concurrency
2. Increase Kinesis shard count
3. Optimize database queries
4. Implement caching

## Validation Checklist

Before considering production ready, verify:

- [ ] All infrastructure deployed
- [ ] CI/CD pipeline working
- [ ] Monitoring dashboards operational
- [ ] Alarms configured and tested
- [ ] Security hardening complete
- [ ] Performance optimized
- [ ] Documentation complete
- [ ] Runbooks created
- [ ] Team trained

## Next Steps

Congratulations! You've completed all modules. You now have:

- ✅ Complete Industry 4.0 manufacturing AI platform
- ✅ Production-ready deployment
- ✅ Comprehensive monitoring and alerting
- ✅ Security and compliance framework

### Continue Learning

1. **Optimize Further**: Fine-tune models and processes
2. **Scale Up**: Expand to more equipment and processes
3. **Integrate**: Connect with existing MES/ERP systems
4. **Share**: Contribute improvements back to the community

---

**Congratulations on completing the Manufacturing AI Workshop! 🎉**

