import ccxt
import time
from src.database.db_manager import get_all_assets, add_price_record
from src.analytics.analyzer import check_volatility

exchange = ccxt.kraken()

def fetch_market_data(asset_id: int, ticker: str) -> None:
    try:
        data = exchange.fetch_ticker(ticker)

        add_price_record(asset_id, data['last'], data['baseVolume'], data['datetime'])

        is_anomaly, change = check_volatility(asset_id)
        if is_anomaly:
            print(f"⚠️ АНОМАЛИЯ по {ticker}! Изменение: {change:.2f}%")

        print(f'''Цена {data['symbol']}: {data['last']} | Объем торгов: {data['baseVolume']}''')

    except Exception as e:
        print(f'Ошибка при сборе {ticker}: {e}')

if __name__ == '__main__':

    assets = get_all_assets()

    while True:
        for asset in assets:
            asset_id, ticker = asset
            fetch_market_data(asset_id, ticker)
            time.sleep(2)
        time.sleep(10)