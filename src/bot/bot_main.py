from aiogram import Bot, Dispatcher
from aiogram.types import Message
from aiogram.filters import Command
import asyncio
from src.config import BOT_TOKEN
from src.database.db_manager import (
    get_all_assets,
    get_last_price,
    add_user,
    add_subscription,
    get_user_subscriptions,
    remove_subscription
)
from datetime import datetime, timezone
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, CallbackQuery

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

@dp.message(Command('subscribe'))
async def subscribe_cmd(msg: Message):
    user_id = msg.from_user.id

    all_assets = get_all_assets()
    user_subscriptions = get_user_subscriptions(user_id)

    builder = InlineKeyboardBuilder()
    has_available_assets = False

    for asset_id, ticker in all_assets:
        if ticker in user_subscriptions:
            continue
        has_available_assets = True
        builder.add(InlineKeyboardButton(
            text=f"➕ {ticker}",
            callback_data=f"sub_{ticker}"
        ))

    builder.adjust(2)

    if not has_available_assets:
        await msg.answer("📋 Ты уже подписан на все доступные в системе активы!")
        return

    await msg.answer(
        "🎯 **Выбери монету для подписки:**",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data and c.data.startswith('sub_'))
async def process_subscribe_callback(callback_query: CallbackQuery):
    ticker = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id

    if add_subscription(user_id, ticker):
        await callback_query.answer(f"Подписка на {ticker} оформлена!")
        await callback_query.message.edit_text(
            f"✅ Ты успешно подписался на уведомления по **{ticker}**!",
            parse_mode="Markdown"
        )
    else:
        await callback_query.answer("Ошибка при оформлении подписки.", show_alert=True)

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

@dp.message(Command('start'))
async def start_cmd(msg: Message):
    user_id = msg.from_user.id
    username = msg.from_user.username
    current_time = datetime.now(timezone.utc).isoformat()

    try:
        add_user(user_id, username, current_time)

        welcome_text = (
            f"👋 **Привет, {msg.from_user.first_name}! Добро пожаловать в Сигнальный Мониторинг.**\n\n"
            f"Ты успешно зарегистрирован в системе. Бот в реальном времени отслеживает "
            f"котировки на бирже Kraken и выявляет математические аномалии.\n\n"
            f"📖 **Интерактивное меню команд (просто нажми на команду):**\n\n"
            f"🎛 **Управление подписками:**\n"
            f"• /subscribe — Открыть меню доступных монет и подписаться на уведомления на инлайн-кнопках.\n"
            f"• /unsubscribe — Показать список твоих активных подписок и отписаться в один клик.\n"
            f"• /subscriptions — Посмотреть сухой список всех активов, за которыми ты сейчас следишь.\n\n"
            f"📊 **Анализ рынка:**\n"
            f"• /status — Быстрый запрос к базе данных. Показывает актуальные сохранённые котировки, объёмы торгов и время последнего тика по всем монетам.\n\n"
            f"🔔 **Как это работает?**\n"
            f"Сборщик постоянно проверяет рынок. Как только фиксируется аномальное изменение цены, "
            f"бот мгновенно присылает тебе алерт. Факт отправки автоматически сохраняется в архиве уведомлений."
        )

        await msg.answer(welcome_text, parse_mode='Markdown')

    except Exception as e:
        print(f'Ошибка при регистрации пользователя {user_id}: {e}')
        await msg.answer('Привет! Произошла ошибка при инициализации твоего профиля. Попробуй позже')

@dp.message(Command('subscriptions'))
async def my_subscriptions_cmd(msg: Message):
    user_id = msg.from_user.id
    subscriptions = get_user_subscriptions(user_id)
    if not subscriptions:
        await msg.answer(
            "⚠️ У тебя пока нет активных подписок.\n\n"
            "Чтобы подписаться, используй: `/subscribe`",
            parse_mode="Markdown"
        )
        return

    response = "📋 **Твои активные подписки:**\n\n"
    for ticker in subscriptions:
        response += f"🔹 `{ticker}`\n"

    response += "\nЧтобы отписаться, отправь: \n/unsubscribe"
    await msg.answer(response, parse_mode="Markdown")

@dp.message(Command('unsubscribe'))
async def unsubscribe_cmd(msg: Message):
    user_id = msg.from_user.id
    user_subs = get_user_subscriptions(user_id)

    if not user_subs:
        await msg.answer(
            "⚠️ У тебя пока нет активных подписок.\n\n"
            "Чтобы подписаться, используй команду /subscribe",
            parse_mode="Markdown"
        )
        return

    builder = InlineKeyboardBuilder()
    for ticker in user_subs:
        builder.add(InlineKeyboardButton(
            text=f"❌ {ticker}",
            callback_data=f"unsub_{ticker}"
        ))

    builder.adjust(2)

    await msg.answer(
        "🗑 **Выбери монету, от которой хочешь отписаться:**",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )

@dp.callback_query(lambda c: c.data and c.data.startswith('unsub_'))
async def process_unsubscribe_callback(callback_query: CallbackQuery):
    ticker = callback_query.data.split('_')[1]
    user_id = callback_query.from_user.id

    if remove_subscription(user_id, ticker):
        await callback_query.answer(f"Отписка от {ticker} выполнена.")
        await callback_query.message.edit_text(
            f"✅ Успешно отписался от уведомлений по **{ticker}**!",
            parse_mode="Markdown"
        )
    else:
        await callback_query.answer("Не удалось удалить подписку.", show_alert=True)

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())