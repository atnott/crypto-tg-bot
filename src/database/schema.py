import sqlite3
from src.config import DB_PATH as db_path

def db_init():

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
    timestamp TEXT
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
    CREATE TABLE IF NOT EXISTS anomalies_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    asset_id INTEGER,
    percent_change REAL NOT NULL,
    price_at_anomaly REAL NOT NULL,
    timestamp TEXT NOT NULL,
    FOREIGN KEY (asset_id) REFERENCES assets(id) ON DELETE CASCADE
    )''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    db_init()
