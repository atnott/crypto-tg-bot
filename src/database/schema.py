import sqlite3
import os

def db_init():

    base_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(base_dir, '..', '..', 'data', 'crypto_bot.sqlite')

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
