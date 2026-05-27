import ccxt
import time
import sqlite3
from src.config import DB_PATH as db_path

exchange = ccxt.kraken()

def fetch_market_data(db_path: str) -> None:
    data = exchange.fetch_ticker('BTC/USDT')

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = '''INSERT INTO price_history (asset_id, price, volume, timestamp) VALUES (?, ?, ?, ?)'''
    cursor.execute(query, (1, data['last'], data['baseVolume'], data['datetime']))

    print(f'''Цена {data['symbol']}: {data['last']} | Объем торгов: {data['baseVolume']}''')

    conn.commit()
    conn.close()

if __name__ == '__main__':

    while True:
        fetch_market_data(db_path)
        time.sleep(10)