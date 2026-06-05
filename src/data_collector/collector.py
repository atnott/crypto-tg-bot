"""Асинхронный сборщик рыночных данных и отправки алертов.

Модуль получает котировки с Kraken через ``ccxt``, сохраняет историю цен,
запускает анализ тренда и отправляет Telegram-уведомления подписчикам при
обнаружении аномальной волатильности.
"""

import ccxt
from src.database.db_manager import get_all_assets, add_price_record, log_analytics, get_subscribers, archive_notification, get_recent_prices
from src.analytics.analyzer import analyze_market_trend
from src.bot.bot_main import bot
import asyncio
from src.database.schema import db_init
from src.database.seed import seed_assets

exchange = ccxt.kraken()

async def fetch_market_data(asset_id: int, ticker: str) -> None:
    """Получает котировку актива, сохраняет её и обрабатывает результат анализа.

    Функция выполняет один цикл обработки для конкретного актива: запрашивает
    тикер на Kraken, сохраняет цену в ``price_history``, передаёт последние цены
    в аналитический модуль и, если обнаружена аномалия, отправляет уведомления
    подписчикам.

    Args:
        asset_id: Идентификатор актива из таблицы ``assets``.
        ticker: Биржевой тикер, используемый в запросе к Kraken.
    """
    try:
        data = exchange.fetch_ticker(ticker)
        price = data['last']
        volume = data['baseVolume']
        timestamp = data['datetime']

        add_price_record(asset_id, price, volume, timestamp)

        rows = get_recent_prices(asset_id, 5)
        prices_list = [row[0] for row in rows]
        direction, is_anomaly, description = analyze_market_trend(prices_list)

        log_analytics(asset_id, direction, int(is_anomaly), description, timestamp)

        if is_anomaly:
            alert_msg = (
                f"⚠️ **АНОМАЛИЯ по `{ticker}`!**\n\n"
                f"📊 Направление тренда: `{direction}`\n"
                f"📝 {description}\n"
                f"💰 Текущая цена: `{price}`\n"
                f"`{timestamp if not timestamp is None else ''}`"
            )

            subscribers = get_subscribers(asset_id)

            for sub_id in subscribers:
                try:
                    await bot.send_message(chat_id=sub_id, text=alert_msg, parse_mode="Markdown")
                    archive_notification(sub_id, alert_msg, timestamp)

                except Exception as send_err:
                    print(f"Не удалось отправить сообщение пользователю {sub_id}: {send_err}")

        print(f'''Цена {data['symbol']}: {data['last']} | Объем торгов: {data['baseVolume']}''')

    except Exception as e:
        print(f'Ошибка при сборе {ticker}: {e}')

async def main_loop():
    """Запускает бесконечный цикл сбора данных по всем активам.

    Перед стартом цикла функция создаёт таблицы, заполняет справочник активов,
    получает список тикеров из базы данных и последовательно обрабатывает их с
    небольшими паузами между запросами.
    """

    db_init()
    seed_assets()

    assets = get_all_assets()
    while True:
        for asset_id, ticker in assets:
            await fetch_market_data(asset_id, ticker)
            await asyncio.sleep(2)
        await asyncio.sleep(10)

if __name__ == '__main__':
    asyncio.run(main_loop())
