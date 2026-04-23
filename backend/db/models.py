# backend/db/models.py
import sqlite3
import json
import os
from datetime import datetime
from typing import Optional, Dict, Any
from config import settings

# Handle database path - try both possible attribute names
if hasattr(settings, 'DATABASE_PATH'):
    DATABASE_PATH = settings.DATABASE_PATH
elif hasattr(settings, 'DATABASE_URL'):
    # Extract path from sqlite:///healthmitra.db format
    DATABASE_PATH = settings.DATABASE_URL.replace("sqlite:///", "")
else:
    # Default fallback
    DATABASE_PATH = "healthmitra.db"

def get_db_connection():
    """Get database connection"""
    # Ensure the directory exists for the database file
    db_dir = os.path.dirname(DATABASE_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)
    
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database with all tables"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Interactions table - stores all user-bot conversations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            phone TEXT NOT NULL,
            message TEXT NOT NULL,
            sender TEXT NOT NULL,
            channel TEXT NOT NULL,
            metadata TEXT,
            timestamp DATETIME NOT NULL
        )
    ''')
    
    # Language statistics table - tracks language usage
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS language_stats (
            language TEXT PRIMARY KEY,
            query_count INTEGER DEFAULT 0,
            last_updated DATETIME NOT NULL
        )
    ''')
    
    # Intent statistics table - tracks types of queries
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS intent_stats (
            intent TEXT PRIMARY KEY,
            query_count INTEGER DEFAULT 0,
            last_updated DATETIME NOT NULL
        )
    ''')
    
    # User activity table - tracks user engagement
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_activity (
            phone TEXT PRIMARY KEY,
            last_active DATETIME NOT NULL,
            query_count INTEGER DEFAULT 0,
            preferred_language TEXT DEFAULT 'en'
        )
    ''')
    
    # Feedback table - stores user feedback
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interaction_id INTEGER,
            rating INTEGER CHECK(rating >= 1 AND rating <= 5),
            feedback_text TEXT,
            timestamp DATETIME NOT NULL,
            FOREIGN KEY (interaction_id) REFERENCES interactions(id)
        )
    ''')
    
    # Outbreak alerts table - stores disease outbreak information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS outbreak_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_id TEXT UNIQUE NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            severity TEXT,
            location TEXT,
            timestamp DATETIME NOT NULL,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    # Subscribers table - users subscribed to alerts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            phone TEXT PRIMARY KEY,
            preferences TEXT,
            subscribed_at DATETIME NOT NULL,
            is_active BOOLEAN DEFAULT 1
        )
    ''')
    
    # Analytics summary table - daily/weekly analytics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS analytics_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,
            total_queries INTEGER DEFAULT 0,
            unique_users INTEGER DEFAULT 0,
            avg_response_time REAL DEFAULT 0,
            UNIQUE(date)
        )
    ''')
    
    # Health tips table - stores health tips and information
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS health_tips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at DATETIME NOT NULL,
            expires_at DATETIME
        )
    ''')
    
    # Emergency contacts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emergency_contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location TEXT NOT NULL,
            service_type TEXT NOT NULL,
            name TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            address TEXT,
            latitude REAL,
            longitude REAL
        )
    ''')
    
    conn.commit()
    
    # Create indexes for better query performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_interactions_phone ON interactions(phone)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_interactions_timestamp ON interactions(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_interactions_sender ON interactions(sender)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_interactions_channel ON interactions(channel)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_outbreak_timestamp ON outbreak_alerts(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_outbreak_status ON outbreak_alerts(status)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_analytics_date ON analytics_summary(date)')
    
    conn.commit()
    conn.close()
    
    print(f"✅ Database initialized successfully at: {DATABASE_PATH}")

def save_interaction(phone: str, message: str, sender: str, channel: str, metadata: Optional[Dict] = None):
    """Save interaction to database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO interactions (phone, message, sender, channel, metadata, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (phone, message, sender, channel, 
              json.dumps(metadata) if metadata else None, 
              datetime.now()))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving interaction: {str(e)}")
        return False

def get_user_stats(phone: str) -> Dict[str, Any]:
    """Get statistics for a specific user"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total queries
        cursor.execute('SELECT COUNT(*) FROM interactions WHERE phone = ? AND sender = "user"', (phone,))
        total_queries = cursor.fetchone()[0]
        
        # Get last active
        cursor.execute('SELECT MAX(timestamp) FROM interactions WHERE phone = ?', (phone,))
        last_active_result = cursor.fetchone()[0]
        last_active = last_active_result if last_active_result else None
        
        # Get preferred language
        cursor.execute('SELECT preferred_language FROM user_activity WHERE phone = ?', (phone,))
        result = cursor.fetchone()
        preferred_language = result[0] if result else 'en'
        
        # Get total interactions
        cursor.execute('SELECT COUNT(*) FROM interactions WHERE phone = ?', (phone,))
        total_interactions = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "phone": phone,
            "total_queries": total_queries,
            "total_interactions": total_interactions,
            "last_active": last_active,
            "preferred_language": preferred_language
        }
    except Exception as e:
        print(f"Error getting user stats: {str(e)}")
        return {
            "phone": phone,
            "total_queries": 0,
            "total_interactions": 0,
            "last_active": None,
            "preferred_language": "en",
            "error": str(e)
        }

def update_language_stats(language: str):
    """Update language usage statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO language_stats (language, query_count, last_updated)
            VALUES (?, 1, ?)
            ON CONFLICT(language) DO UPDATE SET
                query_count = query_count + 1,
                last_updated = excluded.last_updated
        ''', (language, datetime.now()))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating language stats: {str(e)}")
        return False

def update_intent_stats(intent: str):
    """Update intent statistics"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO intent_stats (intent, query_count, last_updated)
            VALUES (?, 1, ?)
            ON CONFLICT(intent) DO UPDATE SET
                query_count = query_count + 1,
                last_updated = excluded.last_updated
        ''', (intent, datetime.now()))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating intent stats: {str(e)}")
        return False

def update_user_activity(phone: str, language: str = 'en'):
    """Update user activity tracking"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO user_activity (phone, last_active, query_count, preferred_language)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(phone) DO UPDATE SET
                last_active = excluded.last_active,
                query_count = query_count + 1,
                preferred_language = excluded.preferred_language
        ''', (phone, datetime.now(), language))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating user activity: {str(e)}")
        return False

def save_feedback(interaction_id: int, rating: int, feedback_text: str = None):
    """Save user feedback"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO feedback (interaction_id, rating, feedback_text, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (interaction_id, rating, feedback_text, datetime.now()))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error saving feedback: {str(e)}")
        return False

def get_analytics_data(days: int = 7):
    """Get analytics data for the last N days"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get total queries in date range
        cursor.execute('''
            SELECT COUNT(*) FROM interactions 
            WHERE sender = 'user' 
            AND timestamp >= datetime('now', ?)
        ''', (f'-{days} days',))
        total_queries = cursor.fetchone()[0]
        
        # Get unique users
        cursor.execute('''
            SELECT COUNT(DISTINCT phone) FROM interactions 
            WHERE timestamp >= datetime('now', ?)
        ''', (f'-{days} days',))
        unique_users = cursor.fetchone()[0]
        
        # Get top intents
        cursor.execute('''
            SELECT intent, query_count FROM intent_stats 
            ORDER BY query_count DESC LIMIT 5
        ''')
        top_intents = cursor.fetchall()
        
        # Get language distribution
        cursor.execute('''
            SELECT language, query_count FROM language_stats 
            ORDER BY query_count DESC
        ''')
        language_dist = cursor.fetchall()
        
        conn.close()
        
        return {
            "total_queries": total_queries,
            "unique_users": unique_users,
            "top_intents": [{"intent": row[0], "count": row[1]} for row in top_intents],
            "language_distribution": [{"language": row[0], "count": row[1]} for row in language_dist]
        }
    except Exception as e:
        print(f"Error getting analytics: {str(e)}")
        return {
            "total_queries": 0,
            "unique_users": 0,
            "top_intents": [],
            "language_distribution": []
        }

def get_recent_interactions(limit: int = 50):
    """Get recent interactions"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT phone, message, sender, channel, timestamp 
            FROM interactions 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        
        interactions = cursor.fetchall()
        conn.close()
        
        return [dict(row) for row in interactions]
    except Exception as e:
        print(f"Error getting recent interactions: {str(e)}")
        return []

def cleanup_old_data(days: int = 90):
    """Clean up old data from database"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Delete old interactions
        cursor.execute('''
            DELETE FROM interactions 
            WHERE timestamp < datetime('now', ?)
        ''', (f'-{days} days',))
        
        # Delete old feedback
        cursor.execute('''
            DELETE FROM feedback 
            WHERE timestamp < datetime('now', ?)
        ''', (f'-{days} days',))
        
        # Delete expired health tips
        cursor.execute('''
            DELETE FROM health_tips 
            WHERE expires_at < datetime('now')
        ''')
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        print(f"Cleaned up {deleted_count} old records")
        return deleted_count
    except Exception as e:
        print(f"Error cleaning up data: {str(e)}")
        return 0

# Initialize database when module is imported
if __name__ != "__main__":
    # Only initialize if not being imported as main module
    try:
        init_db()
    except Exception as e:
        print(f"Note: Database initialization will happen on app startup: {str(e)}")