"""
Authentication and User Management
JWT-based auth with guest session tracking
"""

import jwt
import hashlib
import json
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# JWT Secret (in production, use environment variable)
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key-change-in-production')
JWT_EXPIRATION = 7  # days

# User database file
USER_DB_FILE = 'users.json'
GUEST_SESSIONS_FILE = 'guest_sessions.json'

def load_users():
    """Load users from JSON file"""
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    """Save users to JSON file"""
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def load_guest_sessions():
    """Load guest sessions"""
    if os.path.exists(GUEST_SESSIONS_FILE):
        with open(GUEST_SESSIONS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_guest_sessions(sessions):
    """Save guest sessions"""
    with open(GUEST_SESSIONS_FILE, 'w') as f:
        json.dump(sessions, f, indent=2)

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token(user_id, email):
    """Generate JWT token"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=JWT_EXPIRATION)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def token_required(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return jsonify({'error': 'Token is missing'}), 401
        
        if token.startswith('Bearer '):
            token = token[7:]
        
        payload = verify_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        return f(payload, *args, **kwargs)
    return decorated

# Flask routes (to be added in app.py)

def register_auth_routes(app):
    """Register authentication routes with Flask app"""
    
    @app.route('/api/auth/signup', methods=['POST'])
    def signup():
        """User registration"""
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        name = data.get('name', '')
        age = data.get('age', '')
        gender = data.get('gender', '')
        
        # Validation
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        if '@' not in email or '.' not in email:
            return jsonify({'error': 'Invalid email format'}), 400
        
        if len(password) < 6:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        
        users = load_users()
        
        if email in users:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user_id = str(len(users) + 1)
        users[email] = {
            'user_id': user_id,
            'email': email,
            'password': hash_password(password),
            'name': name,
            'age': age,
            'gender': gender,
            'created_at': datetime.now().isoformat(),
            'chat_history': []
        }
        
        save_users(users)
        
        # Generate token
        token = generate_token(user_id, email)
        
        return jsonify({
            'message': 'Signup successful',
            'token': token,
            'user': {
                'user_id': user_id,
                'email': email,
                    'name': name,
                'age': age,
                'gender': gender
            }
        }), 201
    
    @app.route('/api/auth/login', methods=['POST'])
    def login():
        """User login"""
        data = request.json
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        users = load_users()
        
        if email not in users:
            return jsonify({'error': 'Invalid credentials'}), 401
        
        user = users[email]
        
        if user['password'] != hash_password(password):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        # Generate token
        token = generate_token(user['user_id'], email)
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'email': email,
                'name': user.get('name', ''),
                'age': user.get('age', ''),
                'gender': user.get('gender', '')
            }
        }), 200
    
    @app.route('/api/auth/guest', methods=['POST'])
    def guest_login():
        """Create guest session with message limit"""
        import uuid
        guest_id = str(uuid.uuid4())
        
        guest_sessions = load_guest_sessions()
        guest_sessions[guest_id] = {
            'created_at': datetime.now().isoformat(),
            'message_count': 0,
            'max_messages': 3,
            'chat_history': []
        }
        save_guest_sessions(guest_sessions)
        
        return jsonify({
            'guest_id': guest_id,
            'max_messages': 3,
            'message_count': 0
        }), 200
    
    @app.route('/api/auth/guest/check', methods=['POST'])
    def check_guest_limit():
        """Check if guest has reached message limit"""
        data = request.json
        guest_id = data.get('guest_id', '')
        
        guest_sessions = load_guest_sessions()
        
        if guest_id not in guest_sessions:
            return jsonify({'error': 'Invalid guest session'}), 400
        
        guest = guest_sessions[guest_id]
        remaining = guest['max_messages'] - guest['message_count']
        
        return jsonify({
            'remaining': remaining,
            'max_messages': guest['max_messages'],
            'message_count': guest['message_count'],
            'can_chat': remaining > 0
        }), 200
    
    @app.route('/api/auth/guest/increment', methods=['POST'])
    def increment_guest_count():
        """Increment guest message count"""
        data = request.json
        guest_id = data.get('guest_id', '')
        
        guest_sessions = load_guest_sessions()
        
        if guest_id not in guest_sessions:
            return jsonify({'error': 'Invalid guest session'}), 400
        
        guest_sessions[guest_id]['message_count'] += 1
        save_guest_sessions(guest_sessions)
        
        remaining = guest_sessions[guest_id]['max_messages'] - guest_sessions[guest_id]['message_count']
        
        return jsonify({
            'remaining': remaining,
            'message_count': guest_sessions[guest_id]['message_count']
        }), 200
    
    @app.route('/api/auth/me', methods=['GET'])
    @token_required
    def get_profile(payload):
        """Get user profile"""
        users = load_users()
        email = payload['email']
        
        if email not in users:
            return jsonify({'error': 'User not found'}), 404
        
        user = users[email]
        
        return jsonify({
            'user': {
                'user_id': user['user_id'],
                'email': email,
                'name': user.get('name', ''),
                'age': user.get('age', ''),
                'gender': user.get('gender', ''),
                'created_at': user.get('created_at', '')
            }
        }), 200
    
    @app.route('/api/auth/profile', methods=['PUT'])
    @token_required
    def update_profile(payload):
        """Update user profile"""
        data = request.json
        users = load_users()
        email = payload['email']
        
        if email not in users:
            return jsonify({'error': 'User not found'}), 404
        
        # Update fields
        if 'name' in data:
            users[email]['name'] = data['name']
        if 'age' in data:
            users[email]['age'] = data['age']
        if 'gender' in data:
            users[email]['gender'] = data['gender']
        
        save_users(users)
        
        return jsonify({
            'message': 'Profile updated',
            'user': {
                'user_id': users[email]['user_id'],
                'email': email,
                'name': users[email].get('name', ''),
                'age': users[email].get('age', ''),
                'gender': users[email].get('gender', '')
            }
        }), 200
    
    @app.route('/api/auth/chat-history', methods=['GET'])
    @token_required
    def get_chat_history(payload):
        """Get user's chat history"""
        users = load_users()
        email = payload['email']
        
        if email not in users:
            return jsonify({'error': 'User not found'}), 404
        
        history = users[email].get('chat_history', [])
        
        # Group by date
        grouped = {}
        for chat in history:
            date = chat.get('date', 'Unknown')
            if date not in grouped:
                grouped[date] = []
            grouped[date].append(chat)
        
        return jsonify({
            'history': grouped,
            'all_chats': history
        }), 200
    
    @app.route('/api/auth/chat-history', methods=['POST'])
    @token_required
    def save_chat(payload):
        """Save a chat message to user's history"""
        data = request.json
        users = load_users()
        email = payload['email']
        
        if email not in users:
            return jsonify({'error': 'User not found'}), 404
        
        message_data = {
            'id': data.get('id'),
            'user_message': data.get('user_message'),
            'bot_response': data.get('bot_response'),
            'timestamp': data.get('timestamp'),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'language': data.get('language', 'en')
        }
        
        users[email].setdefault('chat_history', []).append(message_data)
        save_users(users)
        
        return jsonify({'message': 'Chat saved'}), 200
    
    @app.route('/api/auth/logout', methods=['POST'])
    @token_required
    def logout(payload):
        """Logout (client-side token removal)"""
        return jsonify({'message': 'Logged out successfully'}), 200

# Conversation store for users (persistent)
user_conversation_store = {}

def get_user_conversation_history(user_id, session_id=None):
    """Get conversation history for a user"""
    if user_id not in user_conversation_store:
        user_conversation_store[user_id] = {}
    
    if not session_id:
        session_id = 'default'
    
    if session_id not in user_conversation_store[user_id]:
        user_conversation_store[user_id][session_id] = []
    
    return user_conversation_store[user_id][session_id]

def save_user_conversation(user_id, session_id, user_msg, bot_msg):
    """Save conversation for a user"""
    if user_id not in user_conversation_store:
        user_conversation_store[user_id] = {}
    
    if session_id not in user_conversation_store[user_id]:
        user_conversation_store[user_id][session_id] = []
    
    user_conversation_store[user_id][session_id].append({
        'user': user_msg,
        'assistant': bot_msg,
        'timestamp': datetime.now().isoformat()
    })
    
    # Keep only last 50 messages
    if len(user_conversation_store[user_id][session_id]) > 50:
        user_conversation_store[user_id][session_id] = user_conversation_store[user_id][session_id][-50:]
