import sqlite3
from src.config import DB_PATH as db_path

def db_init():

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

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

    conn.commit()
    conn.close()

if __name__ == '__main__':
    db_init()
