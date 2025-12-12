# 🛒 E-Commerce AI Platform

> **Production-ready e-commerce platform with integrated LLM capabilities for intelligent product recommendations, customer support, and business insights**

[![Python](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-blue)](https://reactjs.org/)
[![AWS](https://img.shields.io/badge/AWS-Bedrock-orange)](https://aws.amazon.com/bedrock/)

## 🎯 Overview

This is a complete e-commerce platform demonstrating real-world LLM integration patterns. It showcases how to build AI-powered features that enhance customer experience and business operations.

## ✨ Key Features

### 1. **Smart Product Recommendations**
- Personalized product suggestions based on browsing history
- Collaborative filtering with LLM-enhanced semantic understanding
- Real-time recommendation updates

### 2. **AI Customer Support Chatbot**
- 24/7 intelligent customer support
- Order tracking and status inquiries
- Product information and FAQ handling
- Multi-turn conversation with context awareness

### 3. **Product Description Generation**
- Auto-generate compelling product descriptions
- SEO-optimized content creation
- Multi-language support
- Brand voice customization

### 4. **Review Sentiment Analysis**
- Real-time sentiment analysis of customer reviews
- Automated review moderation
- Insight extraction for product improvements
- Trend analysis across product categories

### 5. **Inventory & Business Insights**
- AI-powered demand forecasting
- Sales trend analysis
- Customer behavior insights
- Automated reporting

## 🏗️ Architecture

See [Architecture Documentation](./architecture.md) for detailed diagrams and explanations.

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- AWS Account (for Bedrock) or OpenAI API Key

### 1. Clone and Setup

```bash
cd ecommerce-retail
# Create .env file (see config/.env.example for template)
cp config/.env.example config/.env
# Edit config/.env with your API keys
```

### 2. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install
```

### 3. Run with Docker

```bash
docker-compose up -d
```

### 4. Access the Application

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:3000/admin

## 📁 Project Structure

```
ecommerce-retail/
├── README.md                 # This file
├── architecture.md           # Solution architecture with diagrams
├── DEPLOYMENT.md            # Deployment guide
├── docker-compose.yml       # Local development setup
├── requirements.txt         # Python dependencies
├── backend/                 # FastAPI backend
│   ├── main.py             # Application entry point
│   ├── api/                # API routes
│   ├── services/           # Business logic
│   ├── models/             # Data models
│   ├── config/             # Configuration
│   └── utils/              # Utilities
├── frontend/               # React frontend
│   ├── src/
│   └── package.json
├── infrastructure/         # Terraform IaC
├── data/                   # Sample data
└── docs/                   # Documentation
```

## 🔧 Configuration

### Environment Variables

See `config/.env.example` for all configuration options.

Key variables:
- `OPENAI_API_KEY` - OpenAI API key
- `AWS_REGION` - AWS region
- `AWS_ACCESS_KEY_ID` - AWS access key
- `AWS_SECRET_ACCESS_KEY` - AWS secret key
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string

## 📚 API Documentation

### Product Recommendations

```python
POST /api/v1/recommendations
{
  "user_id": "user123",
  "product_id": "prod456",
  "context": {
    "browsing_history": [...],
    "purchase_history": [...]
  }
}
```

### Chat Support

```python
POST /api/v1/chat/message
{
  "message": "Where is my order?",
  "session_id": "session123",
  "user_id": "user123"
}
```

### Generate Product Description

```python
POST /api/v1/products/generate-description
{
  "product_name": "Wireless Headphones",
  "features": ["Noise Cancelling", "30hr Battery"],
  "tone": "professional"
}
```

See API documentation at http://localhost:8000/docs for complete reference.

## 🧪 Testing

```bash
# Run backend tests
cd backend
pytest

# Run frontend tests
cd frontend
npm test
```

## 🚀 Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for:
- AWS deployment guide
- Infrastructure setup with Terraform
- CI/CD pipeline configuration
- Production best practices

## 📊 Use Cases

### 1. Personalized Shopping Experience
- AI understands customer preferences
- Real-time product recommendations
- Contextual product suggestions

### 2. Efficient Customer Support
- Instant answers to common questions
- Order status tracking
- Product information queries
- Reduces support ticket volume by 60%

### 3. Content Automation
- Generate product descriptions at scale
- Maintain consistent brand voice
- Multi-language content generation

### 4. Business Intelligence
- Understand customer sentiment
- Identify product improvement opportunities
- Track trends and patterns

## 🔒 Security

- API key management via environment variables
- Rate limiting on all endpoints
- Input validation and sanitization
- CORS configuration
- Authentication and authorization

## 💰 Cost Optimization

- Response caching for common queries
- Model selection based on use case
- Batch processing for bulk operations
- Token usage monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

## 🆘 Support

- [Documentation](./docs/)
- [Architecture Guide](./architecture.md)
- [Deployment Guide](./DEPLOYMENT.md)

---

**Built with ❤️ for real-world LLM integration**
