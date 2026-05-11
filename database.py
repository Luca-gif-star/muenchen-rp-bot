import sqlite3
import os
from datetime import datetime
from config import DATABASE_PATH

def init_database():
    """Initialize all database tables"""
    os.makedirs('data', exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # Counting System
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS counting (
            user_id INTEGER PRIMARY KEY,
            count INTEGER DEFAULT 0,
            last_number INTEGER DEFAULT 0,
            last_timestamp TIMESTAMP
        )
    ''')
    
    # Birthday System
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS birthdays (
            user_id INTEGER PRIMARY KEY,
            birthday TEXT NOT NULL,
            announced INTEGER DEFAULT 0,
            announce_date TEXT
        )
    ''')
    
    # Tickets
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            channel_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            closed_at TIMESTAMP,
            reason TEXT,
            status TEXT DEFAULT 'open'
        )
    ''')
    
    # Team Logs
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS team_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_user_id INTEGER NOT NULL,
            moderator_id INTEGER NOT NULL,
            action TEXT NOT NULL,
            reason TEXT,
            duration TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Warnings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS warnings (
            warn_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            moderator_id INTEGER NOT NULL,
            reason TEXT,
            level INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Verification
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS verification (
            user_id INTEGER PRIMARY KEY,
            verified INTEGER DEFAULT 0,
            verified_at TIMESTAMP
        )
    ''')
    
    # Autoroles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS autoroles (
            role_id INTEGER PRIMARY KEY,
            guild_id INTEGER NOT NULL
        )
    ''')
    
    # Reaction Roles
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reaction_roles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            emoji TEXT NOT NULL,
            role_id INTEGER NOT NULL,
            guild_id INTEGER NOT NULL
        )
    ''')
    
    # Suggestions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS suggestions (
            suggestion_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Ratings
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ratings (
            rating_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            target_user_id INTEGER NOT NULL,
            rating INTEGER NOT NULL,
            comment TEXT,
            category TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Giveaways
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS giveaways (
            giveaway_id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            prize TEXT NOT NULL,
            winner_count INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ends_at TIMESTAMP NOT NULL,
            ended INTEGER DEFAULT 0
        )
    ''')
    
    # Fractions
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fractions (
            user_id INTEGER PRIMARY KEY,
            fraction TEXT NOT NULL,
            rank TEXT NOT NULL,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Embeds
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS saved_embeds (
            embed_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            data TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Polls
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS polls (
            poll_id INTEGER PRIMARY KEY AUTOINCREMENT,
            message_id INTEGER NOT NULL,
            question TEXT NOT NULL,
            options TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ends_at TIMESTAMP NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def get_connection():
    """Get database connection"""
    return sqlite3.connect(DATABASE_PATH)

def add_count(user_id: int, number: int):
    """Add count for user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO counting (user_id, count, last_number, last_timestamp)
        VALUES (?, ?, ?, ?)
    ''', (user_id, number, number, datetime.now()))
    conn.commit()
    conn.close()

def get_count(user_id: int):
    """Get count for user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT count FROM counting WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def add_birthday(user_id: int, birthday: str):
    """Add birthday for user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO birthdays (user_id, birthday)
        VALUES (?, ?)
    ''', (user_id, birthday))
    conn.commit()
    conn.close()

def add_warning(user_id: int, moderator_id: int, reason: str, level: int = 1):
    """Add warning to user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO warnings (user_id, moderator_id, reason, level)
        VALUES (?, ?, ?, ?)
    ''', (user_id, moderator_id, reason, level))
    conn.commit()
    conn.close()

def get_warnings(user_id: int):
    """Get warnings for user"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM warnings WHERE user_id = ?', (user_id,))
    warnings = cursor.fetchall()
    conn.close()
    return warnings

def add_team_log(target_user_id: int, moderator_id: int, action: str, reason: str = None, duration: str = None):
    """Add team log entry"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO team_logs (target_user_id, moderator_id, action, reason, duration)
        VALUES (?, ?, ?, ?, ?)
    ''', (target_user_id, moderator_id, action, reason, duration))
    conn.commit()
    conn.close()
