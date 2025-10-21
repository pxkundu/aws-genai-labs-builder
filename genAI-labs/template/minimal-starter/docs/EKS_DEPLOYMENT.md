# EKS Deployment Guide

This guide walks you through deploying the GenAI Minimal Starter template on Amazon EKS.

## Prerequisites

- AWS CLI configured with appropriate permissions
- kubectl configured to access your EKS cluster
- Docker installed for building container images
- AWS CDK CLI installed (`npm install -g aws-cdk`)

## Infrastructure Setup

### 1. Deploy EKS Cluster with CDK

```bash
cd infrastructure/cdk
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy the stack
cdk deploy
```

### 2. Configure kubectl

```bash
aws eks update-kubeconfig --region us-west-2 --name GenAICluster
```

### 3. Install AWS Load Balancer Controller

```bash
# Install using Helm
helm repo add eks https://aws.github.io/eks-charts
helm repo update
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=GenAICluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller
```

## Application Deployment

### 1. Build and Push Container Image

```bash
# Build the image
docker build -t genai-minimal-starter:latest .

# Tag for ECR
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <ACCOUNT_ID>.dkr.ecr.us-west-2.amazonaws.com

docker tag genai-minimal-starter:latest <ACCOUNT_ID>.dkr.ecr.us-west-2.amazonaws.com/genai-minimal-starter:latest

# Push to ECR
docker push <ACCOUNT_ID>.dkr.ecr.us-west-2.amazonaws.com/genai-minimal-starter:latest
```

### 2. Update Kubernetes Manifests

Update the image reference in `k8s/deployment.yaml`:

```yaml
image: <ACCOUNT_ID>.dkr.ecr.us-west-2.amazonaws.com/genai-minimal-starter:latest
```

### 3. Deploy to EKS

```bash
# Apply all manifests
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/ingress.yaml
```

### 4. Verify Deployment

```bash
# Check pods
kubectl get pods -n genai-minimal-starter

# Check services
kubectl get svc -n genai-minimal-starter

# Check ingress
kubectl get ingress -n genai-minimal-starter
```

## Monitoring and Observability

### 1. Install Prometheus and Grafana

```bash
# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

### 2. View Metrics

```bash
# Port forward to Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Access Grafana at http://localhost:3000
# Default credentials: admin/prom-operator
```

## Scaling

### Horizontal Pod Autoscaler

```bash
kubectl autoscale deployment genai-minimal-starter \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n genai-minimal-starter
```

### Cluster Autoscaler

The EKS cluster is configured with Cluster Autoscaler to automatically scale node groups based on demand.

## Troubleshooting

### Common Issues

1. **Pod not starting**: Check resource limits and requests
2. **Service not accessible**: Verify ingress configuration and ALB controller
3. **Image pull errors**: Ensure ECR permissions and image exists

### Useful Commands

```bash
# Check pod logs
kubectl logs -f deployment/genai-minimal-starter -n genai-minimal-starter

# Describe pod for events
kubectl describe pod <pod-name> -n genai-minimal-starter

# Check ingress status
kubectl describe ingress genai-minimal-starter-ingress -n genai-minimal-starter
```

## Cleanup

```bash
# Delete application
kubectl delete -f k8s/

# Delete infrastructure
cd infrastructure/cdk
cdk destroy
```
