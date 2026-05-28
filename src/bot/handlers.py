from datetime import datetime, timezone

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from src.bot.keyboards import (
    BTN_HELP,
    BTN_STATUS,
    BTN_SUBSCRIBE,
    BTN_SUBSCRIPTIONS,
    BTN_UNSUBSCRIBE,
    after_subscription_keyboard,
    main_menu_keyboard,
    main_navigation_keyboard,
    status_refresh_keyboard,
)
from src.bot.messages import HELP_TEXT, build_welcome_text
from src.database.db_manager import (
    add_subscription,
    add_user,
    get_all_assets,
    get_last_price,
    get_user_subscriptions,
    remove_subscription,
)


router = Router()


async def show_subscribe_menu(msg: Message, user_id: int):
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
        await msg.answer(
            "📋 Ты уже подписан на все доступные в системе активы!",
            reply_markup=main_menu_keyboard,
        )
        return

    await msg.answer(
        "🎯 **Выбери монету для подписки:**",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown"
    )


@router.message(Command('subscribe'))
async def subscribe_cmd(msg: Message):
    await show_subscribe_menu(msg, msg.from_user.id)


@router.callback_query(lambda c: c.data and c.data.startswith('sub_'))
async def process_subscribe_callback(callback_query: CallbackQuery):
    ticker = callback_query.data.split('_', 1)[1]
    user_id = callback_query.from_user.id

    if add_subscription(user_id, ticker):
        await callback_query.answer(f"Подписка на {ticker} оформлена!")
        await callback_query.message.edit_text(
            f"✅ Ты успешно подписался на уведомления по **{ticker}**!",
            reply_markup=after_subscription_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await callback_query.answer("Ошибка при оформлении подписки.", show_alert=True)


def build_status_text() -> str:
    assets = get_all_assets()

    if not assets:
        return 'В базе данных нет отслеживаемых активов'

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

    return "\n".join(response_lines)


@router.message(Command('status'))
async def status_cmd(msg: Message):
    await msg.answer(
        build_status_text(),
        reply_markup=status_refresh_keyboard(),
        parse_mode='Markdown',
    )


@router.message(Command('start'))
async def start_cmd(msg: Message):
    user_id = msg.from_user.id
    username = msg.from_user.username
    current_time = datetime.now(timezone.utc).isoformat()

    try:
        add_user(user_id, username, current_time)

        await msg.answer(
            build_welcome_text(msg.from_user.first_name),
            reply_markup=main_menu_keyboard,
            parse_mode='Markdown',
        )
        await msg.answer(
            "Выбери действие:",
            reply_markup=main_navigation_keyboard(),
        )

    except Exception as e:
        print(f'Ошибка при регистрации пользователя {user_id}: {e}')
        await msg.answer('Привет! Произошла ошибка при инициализации твоего профиля. Попробуй позже')


async def show_subscriptions(msg: Message, user_id: int):
    subscriptions = get_user_subscriptions(user_id)
    if not subscriptions:
        await msg.answer(
            "⚠️ У тебя пока нет активных подписок.\n\n"
            "Чтобы подписаться, нажми кнопку ниже.",
            reply_markup=after_subscription_keyboard(),
            parse_mode="Markdown"
        )
        return

    response = "📋 **Твои активные подписки:**\n\n"
    for ticker in subscriptions:
        response += f"🔹 `{ticker}`\n"

    response += "\nЧтобы отписаться, нажми кнопку ниже."
    await msg.answer(
        response,
        reply_markup=after_subscription_keyboard(),
        parse_mode="Markdown",
    )


@router.message(Command('subscriptions'))
async def my_subscriptions_cmd(msg: Message):
    await show_subscriptions(msg, msg.from_user.id)


async def show_unsubscribe_menu(msg: Message, user_id: int):
    user_subs = get_user_subscriptions(user_id)

    if not user_subs:
        await msg.answer(
            "⚠️ У тебя пока нет активных подписок.\n\n"
            "Чтобы подписаться, нажми кнопку ниже.",
            reply_markup=after_subscription_keyboard(),
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


@router.message(Command('unsubscribe'))
async def unsubscribe_cmd(msg: Message):
    await show_unsubscribe_menu(msg, msg.from_user.id)


@router.callback_query(lambda c: c.data and c.data.startswith('unsub_'))
async def process_unsubscribe_callback(callback_query: CallbackQuery):
    ticker = callback_query.data.split('_', 1)[1]
    user_id = callback_query.from_user.id

    if remove_subscription(user_id, ticker):
        await callback_query.answer(f"Отписка от {ticker} выполнена.")
        await callback_query.message.edit_text(
            f"✅ Успешно отписался от уведомлений по **{ticker}**!",
            reply_markup=after_subscription_keyboard(),
            parse_mode="Markdown"
        )
    else:
        await callback_query.answer("Не удалось удалить подписку.", show_alert=True)


@router.message(Command('help'))
async def help_cmd(msg: Message):
    await msg.answer(
        HELP_TEXT,
        reply_markup=main_navigation_keyboard(),
        parse_mode="Markdown",
    )


@router.message(lambda msg: msg.text == BTN_STATUS)
async def status_button(msg: Message):
    await status_cmd(msg)


@router.message(lambda msg: msg.text == BTN_SUBSCRIBE)
async def subscribe_button(msg: Message):
    await subscribe_cmd(msg)


@router.message(lambda msg: msg.text == BTN_UNSUBSCRIBE)
async def unsubscribe_button(msg: Message):
    await unsubscribe_cmd(msg)


@router.message(lambda msg: msg.text == BTN_SUBSCRIPTIONS)
async def subscriptions_button(msg: Message):
    await my_subscriptions_cmd(msg)


@router.message(lambda msg: msg.text == BTN_HELP)
async def help_button(msg: Message):
    await help_cmd(msg)


@router.callback_query(lambda c: c.data and c.data.startswith('nav_'))
async def process_navigation_callback(callback_query: CallbackQuery):
    action = callback_query.data.split('_', 1)[1]
    msg = callback_query.message
    user_id = callback_query.from_user.id

    await callback_query.answer()

    if action == "status":
        await msg.answer(
            build_status_text(),
            reply_markup=status_refresh_keyboard(),
            parse_mode="Markdown",
        )
    elif action == "subscribe":
        await show_subscribe_menu(msg, user_id)
    elif action == "unsubscribe":
        await show_unsubscribe_menu(msg, user_id)
    elif action == "subscriptions":
        await show_subscriptions(msg, user_id)
    elif action == "menu":
        await msg.answer("Главное меню:", reply_markup=main_navigation_keyboard())
