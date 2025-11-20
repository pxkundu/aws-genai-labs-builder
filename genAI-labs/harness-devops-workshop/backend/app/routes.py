from flask import Blueprint, jsonify, request
from datetime import datetime
import os

api_bp = Blueprint('api', __name__)

# In-memory storage for demo purposes
users_db = [
    {'id': 1, 'name': 'John Doe', 'email': 'john@example.com'},
    {'id': 2, 'name': 'Jane Smith', 'email': 'jane@example.com'},
]

@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': os.getenv('APP_VERSION', '1.0.0'),
        'service': 'backend-api'
    }), 200

@api_bp.route('/users', methods=['GET'])
def get_users():
    """Get list of users"""
    return jsonify({'users': users_db}), 200

@api_bp.route('/users', methods=['POST'])
def create_user():
    """Create a new user"""
    data = request.get_json()
    if not data or 'name' not in data or 'email' not in data:
        return jsonify({'error': 'Name and email are required'}), 400
    
    new_id = max([u['id'] for u in users_db], default=0) + 1
    user = {
        'id': new_id,
        'name': data['name'],
        'email': data['email']
    }
    users_db.append(user)
    return jsonify({'user': user}), 201

@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get user by ID"""
    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user}), 200

@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user by ID"""
    global users_db
    user = next((u for u in users_db if u['id'] == user_id), None)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    users_db = [u for u in users_db if u['id'] != user_id]
    return jsonify({'message': 'User deleted'}), 200

