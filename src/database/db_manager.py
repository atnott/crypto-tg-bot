from src.config import DB_PATH
import sqlite3

def get_all_assets() -> list[tuple]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    assets = cursor.execute('SELECT id, ticker FROM assets').fetchall()

    conn.close()
    return assets

def add_price_record(asset_id: int, price: float, volume: float, timestamp: str) -> None:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    query = '''INSERT INTO price_history (asset_id, price, volume, timestamp) VALUES (?, ?, ?, ?)'''
    cursor.execute(query, (asset_id, price, volume, timestamp))

    conn.commit()
    conn.close()


def get_last_price(asset_id: int) -> tuple:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT price, volume, timestamp 
    FROM price_history 
    WHERE asset_id = ? 
    ORDER BY id DESC 
    LIMIT 1
    ''', (asset_id,))

    row = cursor.fetchone()
    conn.close()
    return row