#!/bin/bash

# Healthcare ChatGPT Clone - EC2 User Data Script
# This script sets up the EC2 instance with Docker, OpenWebUI, and backend API

set -e

# Update system
apt-get update -y
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
./aws/install

# Install Python and pip
apt-get install -y python3 python3-pip python3-venv

# Install additional packages
apt-get install -y git htop tree jq

# Create application directory
mkdir -p /opt/healthcare-chatgpt
cd /opt/healthcare-chatgpt

# Create environment file
cat > .env << EOF
# Database Configuration
DB_HOST=${DB_HOST}
DB_PORT=5432
DB_NAME=${DB_NAME}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}

# S3 Configuration
S3_BUCKET=${S3_BUCKET}
AWS_REGION=${AWS_REGION}

# API Configuration
OPENAI_API_KEY=${OPENAI_API_KEY}
API_PORT=${API_PORT}
OPENWEBUI_PORT=${OPENWEBUI_PORT}

# Application Configuration
ENVIRONMENT=${ENVIRONMENT}
PROJECT_NAME=${PROJECT_NAME}
EOF

# Create Docker Compose file
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  openwebui:
    image: ghcr.io/open-webui/open-webui:main
    container_name: healthcare-openwebui
    ports:
      - "$${OPENWEBUI_PORT:-8080}:8080"
    volumes:
      - openwebui:/app/backend/data
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - WEBUI_SECRET_KEY=your-secret-key-here
      - DEFAULT_USER_ROLE=user
      - ENABLE_SIGNUP=false
      - ENABLE_OAUTH_SIGNUP=false
      - ENABLE_ADMIN_EXPORT=false
      - ENABLE_ADMIN_CHAT_ACCESS=false
      - ENABLE_ADMIN_USER_MANAGEMENT=false
      - ENABLE_ADMIN_SYSTEM_MONITORING=false
      - ENABLE_ADMIN_MODEL_MANAGEMENT=false
      - ENABLE_ADMIN_SETTINGS=false
      - ENABLE_ADMIN_ANALYTICS=false
      - ENABLE_ADMIN_LOGS=false
      - ENABLE_ADMIN_BACKUP=false
      - ENABLE_ADMIN_RESTORE=false
      - ENABLE_ADMIN_IMPORT=false
      - ENABLE_ADMIN_EXPORT=false
      - ENABLE_ADMIN_CHAT_ACCESS=false
      - ENABLE_ADMIN_USER_MANAGEMENT=false
      - ENABLE_ADMIN_SYSTEM_MONITORING=false
      - ENABLE_ADMIN_MODEL_MANAGEMENT=false
      - ENABLE_ADMIN_SETTINGS=false
      - ENABLE_ADMIN_ANALYTICS=false
      - ENABLE_ADMIN_LOGS=false
      - ENABLE_ADMIN_BACKUP=false
      - ENABLE_ADMIN_RESTORE=false
      - ENABLE_ADMIN_IMPORT=false
    restart: unless-stopped
    depends_on:
      - backend-api

  backend-api:
    build: ./backend
    container_name: healthcare-backend-api
    ports:
      - "$${API_PORT:-8000}:8000"
    environment:
      - DB_HOST=${DB_HOST}
      - DB_PORT=${DB_PORT}
      - DB_NAME=${DB_NAME}
      - DB_USER=${DB_USER}
      - DB_PASSWORD=${DB_PASSWORD}
      - S3_BUCKET=${S3_BUCKET}
      - AWS_REGION=${AWS_REGION}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - ENVIRONMENT=${ENVIRONMENT}
    volumes:
      - ./backend:/app
      - /var/run/docker.sock:/var/run/docker.sock
    restart: unless-stopped

volumes:
  openwebui:
EOF

# Create backend directory structure
mkdir -p backend/{api,services,models,config,utils}

# Create backend Dockerfile
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

# Create backend requirements.txt
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
psycopg2-binary==2.9.9
sqlalchemy==2.0.23
alembic==1.12.1
pydantic==2.5.0
pydantic-settings==2.1.0
boto3==1.34.0
openai==1.3.7
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
httpx==0.25.2
aiofiles==23.2.1
jinja2==3.1.2
EOF

# Create basic backend main.py
cat > backend/main.py << 'EOF'
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Healthcare ChatGPT Clone API",
    description="Backend API for Healthcare ChatGPT Clone",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Healthcare ChatGPT Clone API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "healthcare-chatgpt-api"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Set proper permissions
chown -R ubuntu:ubuntu /opt/healthcare-chatgpt
chmod +x /opt/healthcare-chatgpt/docker-compose.yml

# Start services
cd /opt/healthcare-chatgpt
docker-compose up -d

# Create systemd service for auto-start
cat > /etc/systemd/system/healthcare-chatgpt.service << EOF
[Unit]
Description=Healthcare ChatGPT Clone
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/opt/healthcare-chatgpt
ExecStart=/usr/local/bin/docker-compose up -d
ExecStop=/usr/local/bin/docker-compose down
TimeoutStartSec=0

[Install]
WantedBy=multi-user.target
EOF

# Enable and start the service
systemctl enable healthcare-chatgpt.service
systemctl start healthcare-chatgpt.service

# Create log rotation for application logs
cat > /etc/logrotate.d/healthcare-chatgpt << EOF
/opt/healthcare-chatgpt/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
}
EOF

# Create monitoring script
cat > /opt/healthcare-chatgpt/monitor.sh << 'EOF'
#!/bin/bash

# Simple monitoring script
echo "=== Healthcare ChatGPT Clone Status ==="
echo "Date: $(date)"
echo ""

echo "Docker Services:"
docker-compose ps

echo ""
echo "Disk Usage:"
df -h

echo ""
echo "Memory Usage:"
free -h

echo ""
echo "CPU Usage:"
top -bn1 | grep "Cpu(s)"

echo ""
echo "Application Logs (last 10 lines):"
docker-compose logs --tail=10
EOF

chmod +x /opt/healthcare-chatgpt/monitor.sh

# Create cron job for monitoring
echo "*/5 * * * * /opt/healthcare-chatgpt/monitor.sh >> /var/log/healthcare-monitor.log 2>&1" | crontab -

# Log completion
echo "Healthcare ChatGPT Clone setup completed at $(date)" >> /var/log/healthcare-setup.log
