import asyncio

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

from src.bot.handlers import router
from src.config import BOT_TOKEN


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
dp.include_router(router)


async def main():
    await bot.set_my_commands([
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="status", description="Показать статус рынка"),
        BotCommand(command="subscribe", description="Подписаться на актив"),
        BotCommand(command="unsubscribe", description="Отписаться от актива"),
        BotCommand(command="subscriptions", description="Мои подписки"),
        BotCommand(command="help", description="Помощь"),
    ])
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
