from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
from src.config import BOT_TOKEN as token, DB_PATH
import sqlite3

bot = Bot(token=token)
dp = Dispatcher()

@dp.message(Command('start'))
async def start_cmd(msg: Message):
    await msg.answer('Привет! Я сигнальный крипто-бот!')

@dp.message(Command('status'))
async def status_cmd(msg: Message):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute('''SELECT price, volume, timestamp FROM price_history ORDER BY id DESC LIMIT 1''')
    row = cursor.fetchone()

    if not row:
        await msg.answer('Данные еще не собраны!')
        return
    else:
        price, volume, timestamp = row

        response = (
            f"📊 **BTC/USDT**\n\n"
            f"💰 Последняя цена: `{price}`\n"
            f"📈 Объем торгов: `{volume}`\n"
            f"🕒 Время запроса: `{timestamp}`"
        )

        await msg.answer(response, parse_mode='Markdown')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())