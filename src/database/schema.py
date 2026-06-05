import sqlite3
from pathlib import Path
from src.config import DB_PATH as db_path

def db_init():

    Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS assets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT UNIQUE NOT NULL,
    full_name TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS price_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER,
    price REAL,
    volume REAL,
    timestamp TEXT,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT,
    registered_at TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS subscriptions (
    user_id INTEGER,
    asset_id INTEGER,
    PRIMARY KEY (user_id, asset_id),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER,
    predicted_direction TEXT,
    is_anomaly BOOLEAN,
    anomaly_description TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notifications_archive (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    message_text TEXT NOT NULL,
    sent_at TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )''')

    conn.commit()
    conn.close()