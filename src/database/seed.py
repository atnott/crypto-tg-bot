import sqlite3
from src.config import DB_PATH

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.executemany(
    "INSERT OR IGNORE INTO assets (ticker, full_name) VALUES (?, ?)",
    [('BTC/USDT', 'Bitcoin'), ('XRP/USDT', 'Ripple'), ('ETH/USDT', 'Ethereum')],
)

conn.commit()
conn.close()