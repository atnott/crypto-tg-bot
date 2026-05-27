from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
from src.config import BOT_TOKEN
from src.database.db_manager import get_all_assets, get_last_price, add_user, add_subscription
from datetime import datetime, timezone

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command('start'))
async def start_cmd(msg: Message):
    user_id = msg.from_user.id
    username = msg.from_user.username
    current_time = datetime.now(timezone.utc).isoformat()

    try:
        add_user(user_id, username, current_time)
        await msg.answer(
            f"Привет, {msg.from_user.first_name}! Я сигнальный крипто-бот\n"
            "Ты успешно зарегистрирован в системе! Скоро настроим твои подписки"
        )
    except Exception as e:
        print(f'Ошибка при регистрации пользователя {user_id}: {e}')
        await msg.answer('Привет! Произошла ошибка при инициализации твоего профиля. Попробуй позже')

@dp.message(Command('status'))
async def status_cmd(msg: Message):
    assets = get_all_assets()

    if not assets:
        await msg.answer('В базе данных нет отслеживаемых активов')
        return

    response_lines = ["📊 **Актуальный статус рынка:**\n"]

    for asset_id, ticker in assets:
        row = get_last_price(asset_id)

        if row:
            price, volume, timestamp = row
            response_lines.append(
                f"🔹 **{ticker}**\n"
                f"💰 Последняя цена: `{price}`\n"
                f"📈 Объем торгов: `{volume}`\n"
                f"🕒 Время запроса: {timestamp}\n"
            )
        else:
            response_lines.append(f"🔹 **{ticker}**: Данные еще не собраны.\n")

    full_response = "\n".join(response_lines)
    await msg.answer(full_response, parse_mode='Markdown')

@dp.message(Command('subscribe'))
async def subscribe_cmd(msg: Message):
    args = msg.text.split()

    if len(args) < 2:
        await msg.answer("⚠️ Укажите тикер. Пример: `/subscribe btc/usdt`\n\nЧтобы увидеть доступные тикеры, используйте /status", parse_mode="Markdown")
        return

    ticker = args[1].upper()
    user_id = msg.from_user.id

    if add_subscription(user_id, ticker):
        await msg.answer(f"✅ Ты успешно подписался на уведомления по **{ticker}**!", parse_mode="Markdown")
    else:
        await msg.answer(f"❌ Не удалось подписаться. Проверь, правильно ли указан тикер (например, `BTC/USDT`).", parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())