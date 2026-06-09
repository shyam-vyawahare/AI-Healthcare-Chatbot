"""
User Database Management
Simple JSON-based user storage
"""

import json
import os
from datetime import datetime

USERS_FILE = 'users.json'
CHAT_HISTORY_FILE = 'chat_history.json'

def init_db():
    """Initialize database files if they don't exist"""
    if not os.path.exists(USERS_FILE):
        with open(USERS_FILE, 'w') as f:
            json.dump({}, f)
    
    if not os.path.exists(CHAT_HISTORY_FILE):
        with open(CHAT_HISTORY_FILE, 'w') as f:
            json.dump({}, f)

def get_user(email):
    """Get user by email"""
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    return users.get(email)

def get_user_by_id(user_id):
    """Get user by user_id"""
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    for email, user in users.items():
        if user.get('user_id') == user_id:
            return user
    return None

def save_user(email, user_data):
    """Save or update user"""
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    users[email] = user_data
    
    with open(USERS_FILE, 'w') as f:
        json.dump(users, f, indent=2)

def delete_user(email):
    """Delete user"""
    with open(USERS_FILE, 'r') as f:
        users = json.load(f)
    
    if email in users:
        del users[email]
        
        with open(USERS_FILE, 'w') as f:
            json.dump(users, f, indent=2)
        return True
    return False

def get_chat_history(user_id):
    """Get chat history for a user"""
    with open(CHAT_HISTORY_FILE, 'r') as f:
        history = json.load(f)
    return history.get(user_id, [])

def save_chat_history(user_id, session_id, messages):
    """Save chat history for a user"""
    with open(CHAT_HISTORY_FILE, 'r') as f:
        history = json.load(f)
    
    if user_id not in history:
        history[user_id] = {}
    
    history[user_id][session_id] = {
        'messages': messages,
        'updated_at': datetime.now().isoformat()
    }
    
    with open(CHAT_HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=2)

init_db()