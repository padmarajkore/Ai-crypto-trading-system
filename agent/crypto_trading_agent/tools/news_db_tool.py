import sqlite3
import os
from datetime import datetime

DB_PATH = "/Users/padamarajkore/Documents/ADK-crash-course/ai-crypto-trading-system/freqtrade/tradesv3.dryrun.sqlite"

def init_news_table():
    """Initialize the news table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS news_sentiment (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            source TEXT,
            content TEXT,
            sentiment_score REAL,
            impact_level TEXT,
            action_taken TEXT
        )
    ''')
    conn.commit()
    conn.close()

def log_news(source: str, content: str, sentiment_score: float, impact_level: str, action_taken: str = "none"):
    """
    Log a news item and its sentiment to the database.
    """
    init_news_table()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO news_sentiment (source, content, sentiment_score, impact_level, action_taken)
        VALUES (?, ?, ?, ?, ?)
    ''', (source, content, sentiment_score, impact_level, action_taken))
    conn.commit()
    conn.close()
    return "News logged successfully."

def get_recent_news(limit: int = 10):
    """
    Retrieve the most recent news items.
    """
    init_news_table()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        SELECT timestamp, source, content, sentiment_score, impact_level 
        FROM news_sentiment 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    rows = cursor.fetchall()
    conn.close()
    
    news_items = []
    for row in rows:
        news_items.append({
            "timestamp": row[0],
            "source": row[1],
            "content": row[2],
            "sentiment_score": row[3],
            "impact_level": row[4]
        })
    return news_items
