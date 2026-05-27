import ccxt
import time

exchange = ccxt.bybit()

def fetch_market_data():
    data = exchange.fetch_ticker('BTC/USDT')

    print(f'''Цена {data['symbol']}: {data['last']} | Объем торгов: {data['baseVolume']}''')


if __name__ == '__main__':
    while True:
        fetch_market_data()
        time.sleep(10)