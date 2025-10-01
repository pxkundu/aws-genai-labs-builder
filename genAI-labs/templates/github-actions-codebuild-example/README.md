# GitHub Actions + AWS CodeBuild Integration Example

This project demonstrates how to integrate GitHub Actions with AWS CodeBuild to create serverless, hosted GitHub Action Runners with VPC connectivity and IAM integration.

## 🏗️ Architecture

The project includes:
- **GitHub Actions Workflows** for CI/CD
- **AWS CodeBuild Projects** with VPC integration
- **Infrastructure as Code** using AWS CDK, CloudFormation, and Terraform
- **Sample Application** with comprehensive testing
- **Monitoring and Security** configurations

## 🚀 Quick Start

### Prerequisites

1. AWS Account with appropriate permissions
2. GitHub Repository with Actions enabled
3. AWS CLI configured
4. Node.js 18+ and Python 3.11+

### Setup

1. **Clone and Configure**
   ```bash
   git clone <repository-url>
   cd github-actions-codebuild-example
   ```

2. **Configure AWS Credentials**
   ```bash
   aws configure
   ```

3. **Deploy Infrastructure**
   ```bash
   cd infrastructure/cdk
   npm install
   npx cdk bootstrap
   npx cdk deploy --all
   ```

4. **Configure GitHub Secrets**
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_ACCOUNT_ID`

5. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

## 📁 Project Structure

```
github-actions-codebuild-example/
├── .github/workflows/          # GitHub Actions workflows
├── infrastructure/             # Infrastructure as Code
│   ├── cdk/                   # AWS CDK implementation
│   ├── cloudformation/        # CloudFormation templates
│   └── terraform/             # Terraform configuration
├── src/                       # Application source code
│   ├── app/                   # Main application
│   ├── tests/                 # Test suites
│   └── scripts/               # Utility scripts
├── config/                    # Configuration files
├── docs/                      # Documentation
├── scripts/                   # Deployment scripts
└── tests/                     # Integration and E2E tests
```

## 🔧 Configuration

### Environment Variables

```bash
# AWS Configuration
AWS_REGION=us-east-1
AWS_ACCOUNT_ID=123456789012

# Application Configuration
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# Database Configuration
DYNAMODB_TABLE=github-actions-logs
S3_BUCKET=github-actions-artifacts
```

## 🧪 Testing

### Run Tests

```bash
# Unit Tests
cd src && python -m pytest tests/ -v

# Integration Tests
cd tests && python -m pytest integration/ -v

# E2E Tests
cd tests && python -m pytest e2e/ -v
```

## 📊 Monitoring

The project includes comprehensive monitoring:
- CloudWatch Dashboards
- CloudWatch Alarms
- Cost Optimization
- Performance Metrics

## 🔒 Security

Security features include:
- VPC isolation
- IAM least privilege
- Encryption at rest and in transit
- Security scanning
- Vulnerability assessment

## 📚 Documentation

- [Setup Guide](docs/setup.md)
- [Architecture Overview](docs/architecture.md)
- [Troubleshooting](docs/troubleshooting.md)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.
