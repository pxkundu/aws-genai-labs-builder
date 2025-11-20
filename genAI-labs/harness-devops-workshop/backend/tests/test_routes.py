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
    assert 'timestamp' in data
    assert 'version' in data

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
    assert data['user']['email'] == user_data['email']

def test_create_user_missing_fields(client):
    """Test create user with missing fields"""
    response = client.post('/api/users', json={'name': 'Test'})
    assert response.status_code == 400

def test_get_user_by_id(client):
    """Test get user by ID"""
    response = client.get('/api/users/1')
    assert response.status_code == 200
    data = response.get_json()
    assert 'user' in data
    assert data['user']['id'] == 1

def test_get_user_not_found(client):
    """Test get non-existent user"""
    response = client.get('/api/users/999')
    assert response.status_code == 404

