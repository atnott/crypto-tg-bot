import ccxt
import time
import sqlite3
from src.config import DB_PATH as db_path

exchange = ccxt.kraken()

def fetch_market_data(db_path: str, asset_id: int, ticker: str) -> None:
    data = exchange.fetch_ticker(ticker)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    query = '''INSERT INTO price_history (asset_id, price, volume, timestamp) VALUES (?, ?, ?, ?)'''
    cursor.execute(query, (asset_id, data['last'], data['baseVolume'], data['datetime']))

    print(f'''Цена {data['symbol']}: {data['last']} | Объем торгов: {data['baseVolume']}''')

    conn.commit()
    conn.close()

if __name__ == '__main__':

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    assets = cursor.execute('SELECT id, ticker FROM assets').fetchall()

    while True:
        for asset in assets:
            asset_id, ticker = asset
            fetch_market_data(db_path, asset_id, ticker)
            time.sleep(2)
        time.sleep(10)