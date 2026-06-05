"""Функции доступа к SQLite-базе проекта.

Модуль скрывает SQL-запросы от Telegram-бота и сборщика данных. Остальные
части приложения работают с пользователями, активами, подписками, ценами,
аналитикой и архивом уведомлений через эти функции.
"""

from src.config import DB_PATH
import sqlite3
from datetime import datetime, timezone

def get_all_assets() -> list[tuple]:
    """Возвращает все активы, доступные для мониторинга.

    Returns:
        Список кортежей ``(asset_id, ticker)`` из таблицы ``assets``.
    """
    conn = sqlite3.connect(DB_PATH, timeout=20)
    cursor = conn.cursor()

    assets = cursor.execute('SELECT id, ticker FROM assets').fetchall()

    conn.close()
    return assets

def add_price_record(asset_id: int, price: float, volume: float, timestamp: str) -> None:
    """Сохраняет новую запись истории цены.

    Args:
        asset_id: Идентификатор актива из таблицы ``assets``.
        price: Последняя полученная цена актива.
        volume: Объём торгов, полученный от биржи.
        timestamp: Время получения котировки. Если значение пустое, используется
            текущее UTC-время.
    """
    conn = sqlite3.connect(DB_PATH, timeout=20)
    cursor = conn.cursor()

    if not timestamp:
        timestamp = datetime.now(timezone.utc).isoformat()

    query = '''INSERT INTO price_history (asset_id, price, volume, timestamp) VALUES (?, ?, ?, ?)'''
    cursor.execute(query, (asset_id, price, volume, timestamp))

    conn.commit()
    conn.close()


def get_last_price(asset_id: int) -> tuple:
    """Возвращает последнюю сохранённую цену актива.

    Args:
        asset_id: Идентификатор актива из таблицы ``assets``.

    Returns:
        Кортеж ``(price, volume, timestamp)`` или ``None``, если история для
        актива ещё не собрана.
    """
    conn = sqlite3.connect(DB_PATH, timeout=20)
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
    """Возвращает последние цены актива в хронологическом порядке.

    Args:
        asset_id: Идентификатор актива из таблицы ``assets``.
        limit: Максимальное количество записей истории цены.

    Returns:
        Список кортежей ``(price, timestamp)``, отсортированный от старых
        записей к новым.
    """
    conn = sqlite3.connect(DB_PATH, timeout=20)
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
    """Регистрирует пользователя Telegram, если он ещё не сохранён.

    Args:
        user_id: Telegram ID пользователя.
        username: Telegram username или ``None``, если username не задан.
        registered_at: Время регистрации в ISO-формате.
    """
    conn = sqlite3.connect(DB_PATH, timeout=20)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    query = '''INSERT OR IGNORE INTO users (id, username, registered_at) VALUES (?, ?, ?)'''
    cursor.execute(query, (user_id, username, registered_at))

    conn.commit()
    conn.close()

def add_subscription(user_id: int, ticker: str) -> bool:
    """Подписывает пользователя на актив по тикеру.

    Args:
        user_id: Telegram ID пользователя.
        ticker: Тикер актива из справочника ``assets``.

    Returns:
        ``True``, если актив найден и операция записи выполнена успешно.
        ``False``, если тикер не найден или SQLite вернул ошибку.
    """
    conn = sqlite3.connect(DB_PATH, timeout=20)
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
    """Возвращает Telegram ID пользователей, подписанных на актив.

    Args:
        asset_id: Идентификатор актива из таблицы ``assets``.

    Returns:
        Список Telegram ID из таблицы ``subscriptions``.
    """
    conn = sqlite3.connect(DB_PATH, timeout=20)
    cursor = conn.cursor()

    cursor.execute('''SELECT user_id FROM subscriptions WHERE asset_id = ?''', (asset_id,))
    rows = cursor.fetchall()

    conn.close()
    return [row[0] for row in rows]

def log_analytics(asset_id: int, direction: str, is_anomaly: bool, description: str, created_at: str) -> None:
    """Сохраняет результат анализа рынка.

    Args:
        asset_id: Идентификатор актива из таблицы ``assets``.
        direction: Классификация направления движения цены.
        is_anomaly: Признак аномального изменения цены.
        description: Текстовое описание результата анализа.
        created_at: Время создания результата. Если значение пустое,
            используется текущее UTC-время.
    """
    conn = sqlite3.connect(DB_PATH, timeout=20)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    if not created_at:
        created_at = datetime.now(timezone.utc).isoformat()

    query = '''
        INSERT INTO analytics (asset_id, predicted_direction, is_anomaly, anomaly_description, created_at) 
        VALUES (?, ?, ?, ?, ?)
    '''
    cursor.execute(query, (asset_id, direction, is_anomaly, description, created_at))

    conn.commit()
    conn.close()

def archive_notification(user_id: int, message_text: str, sent_at: str) -> None:
    """Сохраняет факт отправки уведомления пользователю.

    Args:
        user_id: Telegram ID пользователя, которому отправлено сообщение.
        message_text: Текст отправленного уведомления.
        sent_at: Время отправки. Если значение пустое, используется текущее
            UTC-время.
    """
    conn = sqlite3.connect(DB_PATH, timeout=20)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    if not sent_at:
        from datetime import datetime, timezone
        sent_at = datetime.now(timezone.utc).isoformat()

    query = '''
            INSERT INTO notifications_archive (user_id, message_text, sent_at) 
            VALUES (?, ?, ?)
        '''
    cursor.execute(query, (user_id, message_text, sent_at))

    conn.commit()
    conn.close()


def get_user_subscriptions(user_id: int) -> list[str]:
    """Возвращает тикеры активов, на которые подписан пользователь.

    Args:
        user_id: Telegram ID пользователя.

    Returns:
        Список тикеров из справочника ``assets``.
    """
    conn = sqlite3.connect(DB_PATH, timeout=20)
    cursor = conn.cursor()

    query = '''
    SELECT a.ticker 
    FROM subscriptions s
    JOIN assets a ON s.asset_id = a.id
    WHERE s.user_id = ?
    '''
    cursor.execute(query, (user_id,))
    rows = cursor.fetchall()

    conn.close()
    return [row[0] for row in rows]

def remove_subscription(user_id: int, ticker: str) -> bool:
    """Удаляет подписку пользователя на актив.

    Args:
        user_id: Telegram ID пользователя.
        ticker: Тикер актива, от которого нужно отписаться.

    Returns:
        ``True``, если подписка была удалена. ``False``, если тикер не найден
        или у пользователя не было такой подписки.
    """
    conn = sqlite3.connect(DB_PATH, timeout=20)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("SELECT id FROM assets WHERE ticker = ?", (ticker.upper(),))
    asset_row = cursor.fetchone()

    if not asset_row:
        conn.close()
        return False

    asset_id = asset_row[0]

    cursor.execute(
        "DELETE FROM subscriptions WHERE user_id = ? AND asset_id = ?",
        (user_id, asset_id)
    )

    changes = conn.total_changes
    conn.commit()
    conn.close()

    return changes > 0
