## Minimal Starter (EKS-Optimized FastAPI Backend)

A production-ready FastAPI backend template optimized for Amazon EKS deployment with comprehensive infrastructure as code.

### Features

- **FastAPI Backend**: Production-ready API with health checks
- **EKS Deployment**: Complete Kubernetes manifests and AWS CDK infrastructure
- **Security**: Non-root container user, multi-stage builds
- **Monitoring**: Prometheus metrics, HPA, and observability
- **Scalability**: Auto-scaling with ALB ingress controller
- **Local Development**: Docker Compose for quick testing

### Quickstart

#### Local Development
1. Create a `.env` file based on `.env.example`
2. Run with Docker Compose:
```bash
docker compose up --build
```
3. Visit `http://localhost:8000/health` to verify

#### EKS Deployment
1. Deploy infrastructure: `cd infrastructure/cdk && cdk deploy`
2. Build and push container: See `docs/EKS_DEPLOYMENT.md`
3. Deploy to EKS: `kubectl apply -f k8s/`

### Project Structure

```
minimal-starter/
  ├── Dockerfile                    # Multi-stage, EKS-optimized
  ├── docker-compose.yml            # Local development
  ├── .env.example                  # Environment configuration
  ├── backend/                      # FastAPI application
  │   ├── main.py
  │   └── requirements.txt
  ├── k8s/                          # Kubernetes manifests
  │   ├── namespace.yaml
  │   ├── configmap.yaml
  │   ├── deployment.yaml
  │   ├── service.yaml
  │   ├── ingress.yaml
  │   ├── hpa.yaml                  # Horizontal Pod Autoscaler
  │   └── monitoring.yaml           # Prometheus ServiceMonitor
  ├── infrastructure/               # AWS CDK Infrastructure
  │   └── cdk/
  │       ├── app.py
  │       ├── genai_minimal_starter_stack.py
  │       ├── requirements.txt
  │       └── cdk.json
  └── docs/
      ├── README.md
      └── EKS_DEPLOYMENT.md         # Complete EKS deployment guide
```


