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

def get_recent_prices(asset_id: int, limit: int = 10) -> list[tuple]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''
    SELECT price, timestamp 
    FROM price_history 
    WHERE asset_id = ? 
    ORDER BY id DESC 
    LIMIT ?
    ''', (asset_id, limit))

    rows = cursor.fetchall()
    conn.close()

    return rows[::-1]

def add_user(user_id: int, username: str | None, registered_at: str) -> None:
    """Регистрирует нового пользователя в базе данных, если его там еще нет"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    query = '''INSERT OR IGNORE INTO users (id, username, registered_at) VALUES (?, ?, ?)'''
    cursor.execute(query, (user_id, username, registered_at))

    conn.commit()
    conn.close()

def add_subscription(user_id: int, ticker: str) -> bool:
    """Подписывает пользователя на монету по её тикеру. Возвращает True в случае успеха"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute('''SELECT id FROM assets WHERE ticker = ?''', (ticker.upper(),))
    asset_row = cursor.fetchone()

    if not asset_row:
        conn.close()
        return False

    asset_id = asset_row[0]

    try:
        cursor.execute(
            "INSERT OR IGNORE INTO subscriptions (user_id, asset_id) VALUES (?, ?)",
            (user_id, asset_id)
        )

        conn.commit()
        success = True
    except sqlite3.Error:
        success = False

    conn.close()
    return success

def get_subscribers(asset_id: int) -> list[int]:
    """Возвращает список Telegram ID пользователей, подписанных на данный актив"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''SELECT user_id FROM subscriptions WHERE asset_id = ?''', (asset_id,))
    rows = cursor.fetchall()

    conn.close()
    return [row[0] for row in rows]