import ccxt
import time
from src.database.db_manager import get_all_assets, add_price_record
from src.analytics.analyzer import check_volatility
from src.bot.bot_main import bot
from src.config import ADMIN_ID

exchange = ccxt.kraken()

async def fetch_market_data(asset_id: int, ticker: str) -> None:
    try:
        data = exchange.fetch_ticker(ticker)
        price = data['last']
        volume = data['baseVolume']
        timestamp = data['datetime']

        add_price_record(asset_id, price, volume, timestamp)

        is_anomaly, change = check_volatility(asset_id)
        if is_anomaly:

            alert_msg = (
                f"⚠️ **АНОМАЛИЯ по {ticker}!**\n\n"
                f"📈 Изменение: `{change:.2f}%`\n"
                f"💰 Текущая цена: `{price}`\n"
                f"🕒 Время: {timestamp}"
            )

            from src.database.db_manager import get_subscribers
            subscribers = get_subscribers(asset_id)

            for sub_id in subscribers:
                try:
                    await bot.send_message(chat_id=sub_id, text=alert_msg, parse_mode="Markdown")
                except Exception as send_err:
                    print(f"Не удалось отправить сообщение пользователю {sub_id}: {send_err}")

        print(f'''Цена {data['symbol']}: {data['last']} | Объем торгов: {data['baseVolume']}''')

    except Exception as e:
        print(f'Ошибка при сборе {ticker}: {e}')

async def main_loop():
    assets = get_all_assets()
    while True:
        for asset_id, ticker in assets:
            await fetch_market_data(asset_id, ticker)
            await asyncio.sleep(2)
        await asyncio.sleep(10)

if __name__ == '__main__':
    import asyncio
    asyncio.run(main_loop())