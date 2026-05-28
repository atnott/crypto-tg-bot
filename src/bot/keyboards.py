from aiogram.types import InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


BTN_STATUS = "📊 Статус рынка"
BTN_SUBSCRIBE = "➕ Подписаться"
BTN_UNSUBSCRIBE = "➖ Отписаться"
BTN_SUBSCRIPTIONS = "📋 Мои подписки"
BTN_HELP = "ℹ️ Помощь"

main_menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text=BTN_STATUS), KeyboardButton(text=BTN_SUBSCRIPTIONS)],
        [KeyboardButton(text=BTN_SUBSCRIBE), KeyboardButton(text=BTN_UNSUBSCRIBE)],
        [KeyboardButton(text=BTN_HELP)],
    ],
    resize_keyboard=True,
)


def main_navigation_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📊 Статус", callback_data="nav_status"),
        InlineKeyboardButton(text="➕ Подписаться", callback_data="nav_subscribe"),
    )
    builder.row(
        InlineKeyboardButton(text="📋 Мои подписки", callback_data="nav_subscriptions"),
        InlineKeyboardButton(text="➖ Отписаться", callback_data="nav_unsubscribe"),
    )
    return builder.as_markup()


def after_subscription_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="➕ Подписаться ещё", callback_data="nav_subscribe"),
        InlineKeyboardButton(text="📋 Мои подписки", callback_data="nav_subscriptions"),
    )
    builder.row(
        InlineKeyboardButton(text="➖ Отписаться", callback_data="nav_unsubscribe"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="nav_menu"),
    )
    return builder.as_markup()


def status_refresh_keyboard():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🔄 Обновить", callback_data="nav_status"))
    builder.row(
        InlineKeyboardButton(text="➕ Подписаться", callback_data="nav_subscribe"),
        InlineKeyboardButton(text="🏠 Главное меню", callback_data="nav_menu"),
    )
    return builder.as_markup()
