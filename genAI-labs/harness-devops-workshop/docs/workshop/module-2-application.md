# Module 2: Application Development

## Overview

In this module, you'll build a sample microservices application with a Python Flask backend and a React frontend. This application will be deployed through Harness pipelines in subsequent modules.

**Duration**: 90 minutes  
**Difficulty**: Beginner

## Learning Objectives

By the end of this module, you will:
- Create a Python Flask REST API backend
- Build a React frontend application
- Configure Docker containers for both services
- Write unit and integration tests
- Set up local development environment

## Prerequisites

- Python 3.11+ installed
- Node.js 18+ installed
- Docker installed
- Code editor (VS Code recommended)
- Git installed

## Step 1: Project Structure

### 1.1 Create Directory Structure

```bash
mkdir -p harness-devops-workshop
cd harness-devops-workshop
mkdir -p backend frontend tests infrastructure harness scripts
```

### 1.2 Initialize Git Repository

```bash
git init
git remote add origin <your-github-repo-url>
```

## Step 2: Backend Application (Python Flask)

### 2.1 Create Backend Structure

```bash
cd backend
mkdir -p app tests
```

### 2.2 Create requirements.txt

Create `backend/requirements.txt`:

```txt
Flask==3.0.0
Flask-CORS==4.0.0
gunicorn==21.2.0
pytest==7.4.3
pytest-cov==4.1.0
requests==2.31.0
python-dotenv==1.0.0
```

### 2.3 Create Main Application

Create `backend/app/__init__.py`:

```python
from flask import Flask
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### 2.4 Create API Routes

Create `backend/app/routes.py`:

```python
from flask import Blueprint, jsonify, request
from datetime import datetime
import os

api_bp = Blueprint('api', __name__)

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': os.getenv('APP_VERSION', '1.0.0')
    }), 200

@api_bp.route('/users', methods=['GET'])
def get_users():
    """Get list of users"""
    users = [
        {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
        {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'},
    ]
    return jsonify({'users': users}), 200

@api_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Name and email are required'}), 400
    
    user = {
        'id': len(get_users()[0].get_json()['users']) + 1,
        'name': data['name'],
        'email': data['email']
    }
    return jsonify({'user': user}), 201

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    users = get_users()[0].get_json()['users']
    user = next((u for u in users if u['id'] == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user}), 200
```

### 2.5 Create Dockerfile

Create `backend/Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app
ENV PYTHONUNBUFFERED=1

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:create_app()"]
```

### 2.6 Create Tests

Create `backend/tests/test_routes.py`:

```python
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test health check endpoint"""
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'

def test_get_users(client):
    """Test get users endpoint"""
    response = client.get('/api/users')
    assert response.status_code == 200
    data = response.get_json()
    assert 'users' in data
    assert len(data['users']) > 0

def test_create_user(client):
    """Test create user endpoint"""
    user_data = {
        'name': 'Test User',
        'email': 'test@example.com'
    }
    response = client.post('/api/users', json=user_data)
    assert response.status_code == 201
    data = response.get_json()
    assert 'user' in data
    assert data['user']['name'] == user_data['name']
```

## Step 3: Frontend Application (React)

### 3.1 Initialize React App

```bash
cd frontend
npx create-react-app . --template typescript
```

### 3.2 Create API Service

Create `frontend/src/services/api.ts`:

```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

export interface User {
  id: number;
  name: string;
  email: string;
}

export const api = {
  async getHealth(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  },

  async getUsers(): Promise<User[]> {
    const response = await fetch(`${API_BASE_URL}/users`);
    const data = await response.json();
    return data.users;
  },

  async createUser(user: Omit<User, 'id'>): Promise<User> {
    const response = await fetch(`${API_BASE_URL}/users`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(user),
    });
    const data = await response.json();
    return data.user;
  },
};
```

### 3.3 Create User Component

Create `frontend/src/components/UserList.tsx`:

```typescript
import React, { useEffect, useState } from 'react';
import { api, User } from '../services/api';

export const UserList: React.FC = () => {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const data = await api.getUsers();
      setUsers(data);
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div>
      <h2>Users</h2>
      <ul>
        {users.map((user) => (
          <li key={user.id}>
            {user.name} - {user.email}
          </li>
        ))}
      </ul>
    </div>
  );
};
```

### 3.4 Update App Component

Update `frontend/src/App.tsx`:

```typescript
import React from 'react';
import { UserList } from './components/UserList';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Harness DevOps Workshop</h1>
        <UserList />
      </header>
    </div>
  );
}

export default App;
```

### 3.5 Create Dockerfile

Create `frontend/Dockerfile`:

```dockerfile
# Build stage
FROM node:18-alpine as build

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built files
COPY --from=build /app/build /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
```

### 3.6 Create nginx Configuration

Create `frontend/nginx.conf`:

```nginx
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location /api {
        proxy_pass http://backend:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## Step 4: Docker Compose for Local Development

### 4.1 Create docker-compose.yml

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
      - APP_VERSION=1.0.0
    volumes:
      - ./backend/app:/app/app
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://localhost:5000/api
```

## Step 5: Testing

### 5.1 Backend Tests

```bash
cd backend
pip install -r requirements.txt
pytest tests/ -v --cov=app
```

### 5.2 Frontend Tests

```bash
cd frontend
npm install
npm test
```

### 5.3 Local Development

```bash
# Start services
docker-compose up --build

# Test backend
curl http://localhost:5000/api/health

# Test frontend
open http://localhost
```

## Step 6: Git Configuration

### 6.1 Create .gitignore

Create `.gitignore`:

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Docker
.dockerignore

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local
```

### 6.2 Commit Code

```bash
git add .
git commit -m "Initial application setup"
git push origin main
```

## Troubleshooting

### Backend Issues
- **Port already in use**: Change port in docker-compose.yml
- **Import errors**: Verify Python path and virtual environment
- **Tests failing**: Check test data and API responses

### Frontend Issues
- **Build errors**: Check Node.js version and dependencies
- **API connection**: Verify API_BASE_URL environment variable
- **CORS errors**: Ensure Flask-CORS is configured

## Next Steps

Congratulations! You've completed Module 2. You now have:
- ✅ Backend API application
- ✅ Frontend React application
- ✅ Docker containers configured
- ✅ Tests written
- ✅ Local development environment

**Proceed to [Module 3: Infrastructure as Code](./module-3-infrastructure.md)** to provision AWS infrastructure! 🚀

