# Healthcare ChatGPT Clone

A comprehensive ChatGPT clone application for healthcare organizations using OpenWebUI, OpenAI API, and AWS Bedrock.

## 🏥 Overview

AI-powered chat interface for healthcare providers with HIPAA-compliant architecture, customizable responses, and enterprise-grade security.

## 🚀 Key Features

- Multi-LLM Support (OpenAI + AWS Bedrock)
- Healthcare Knowledge Base (S3-hosted)
- Secure Chat Storage (RDS Aurora PostgreSQL)
- HIPAA Compliance
- One-click Terraform Deployment
- Customizable for any healthcare organization

## 📁 Project Structure

```
healthcare/
├── README.md                    # This file
├── architecture.md              # Solution architecture
├── DEPLOYMENT.md               # Deployment guide
├── CUSTOMIZATION.md            # Customization guide
├── docker-compose.yml          # Local development
├── Dockerfile                  # OpenWebUI container
├── requirements.txt            # Python dependencies
├── infrastructure/             # Terraform infrastructure
├── backend/                    # Backend API services
├── frontend/                   # OpenWebUI customization
├── data/                       # Knowledge base and sample data
├── scripts/                    # Deployment scripts
├── tests/                      # Test suite
└── docs/                       # Documentation
```

## 🛠 Technology Stack

- **Frontend**: OpenWebUI (Docker)
- **Backend**: Python FastAPI
- **Database**: AWS RDS Aurora PostgreSQL
- **Storage**: AWS S3
- **AI/LLM**: OpenAI API + AWS Bedrock
- **Infrastructure**: Terraform + AWS

## 🚀 Quick Start

1. Deploy infrastructure: `cd infrastructure && terraform apply`
2. Deploy application: `./scripts/deployment/deploy.sh`
3. Access: `http://your-ec2-ip:8080`

## 📚 Documentation

- [Architecture Guide](architecture.md)
- [Deployment Guide](DEPLOYMENT.md)
- [Customization Guide](CUSTOMIZATION.md)
- [API Documentation](docs/api/)

## 🔒 Security

HIPAA-compliant with encrypted data, VPC isolation, and comprehensive monitoring.