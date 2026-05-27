from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import asyncio

token = '8818754908:AAGjWKLA8Ki_kLIdlpodbihBW_uQkZIqIhY'

bot = Bot(token=token)
dp = Dispatcher()

@dp.message(Command('start'))
async def start_cmd(msg: Message):
    await msg.answer('Привет! Я сигнальный крипто-бот!')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())