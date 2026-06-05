import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

from src.bot import handlers


def make_callback(data: str):
    return SimpleNamespace(
        data=data,
        from_user=SimpleNamespace(id=42),
        message=SimpleNamespace(edit_text=AsyncMock()),
        answer=AsyncMock(),
    )


def test_process_subscribe_callback_edits_message_after_success(monkeypatch):
    callback = make_callback("sub_BTC/USDT")
    keyboard = object()
    add_subscription_calls = []

    def add_subscription(user_id, ticker):
        add_subscription_calls.append((user_id, ticker))
        return True

    monkeypatch.setattr(handlers, "add_subscription", add_subscription)
    monkeypatch.setattr(handlers, "build_subscribe_keyboard", lambda user_id: keyboard)

    asyncio.run(handlers.process_subscribe_callback(callback))

    assert add_subscription_calls == [(42, "BTC/USDT")]
    callback.answer.assert_awaited_once_with("Подписка на BTC/USDT оформлена!")
    callback.message.edit_text.assert_awaited_once()

    args, kwargs = callback.message.edit_text.await_args
    assert "BTC/USDT" in args[0]
    assert "Выбери следующую монету" in args[0]
    assert kwargs["reply_markup"] is keyboard
    assert kwargs["parse_mode"] == "Markdown"


def test_process_subscribe_callback_shows_all_subscribed_state(monkeypatch):
    callback = make_callback("sub_ETH/USDT")

    monkeypatch.setattr(handlers, "add_subscription", lambda user_id, ticker: True)
    monkeypatch.setattr(handlers, "build_subscribe_keyboard", lambda user_id: None)

    asyncio.run(handlers.process_subscribe_callback(callback))

    callback.answer.assert_awaited_once_with("Подписка на ETH/USDT оформлена!")
    callback.message.edit_text.assert_awaited_once()

    args, kwargs = callback.message.edit_text.await_args
    assert "ETH/USDT" in args[0]
    assert "подписан на все доступные" in args[0]
    assert kwargs["reply_markup"] is not None
    assert kwargs["parse_mode"] == "Markdown"


def test_process_subscribe_callback_answers_with_alert_on_failure(monkeypatch):
    callback = make_callback("sub_UNKNOWN/USDT")

    monkeypatch.setattr(handlers, "add_subscription", lambda user_id, ticker: False)

    asyncio.run(handlers.process_subscribe_callback(callback))

    callback.answer.assert_awaited_once_with(
        "Ошибка при оформлении подписки.",
        show_alert=True,
    )
    callback.message.edit_text.assert_not_awaited()


def test_process_unsubscribe_callback_edits_message_after_success(monkeypatch):
    callback = make_callback("unsub_BTC/USDT")
    keyboard = object()
    remove_subscription_calls = []

    def remove_subscription(user_id, ticker):
        remove_subscription_calls.append((user_id, ticker))
        return True

    monkeypatch.setattr(handlers, "remove_subscription", remove_subscription)
    monkeypatch.setattr(
        handlers,
        "build_unsubscribe_view",
        lambda user_id: ("Остались подписки", keyboard),
    )

    asyncio.run(handlers.process_unsubscribe_callback(callback))

    assert remove_subscription_calls == [(42, "BTC/USDT")]
    callback.answer.assert_awaited_once_with("Отписка от BTC/USDT выполнена.")
    callback.message.edit_text.assert_awaited_once()

    args, kwargs = callback.message.edit_text.await_args
    assert "BTC/USDT" in args[0]
    assert "Остались подписки" in args[0]
    assert kwargs["reply_markup"] is keyboard
    assert kwargs["parse_mode"] == "Markdown"


def test_process_unsubscribe_callback_answers_with_alert_on_failure(monkeypatch):
    callback = make_callback("unsub_UNKNOWN/USDT")

    monkeypatch.setattr(handlers, "remove_subscription", lambda user_id, ticker: False)

    asyncio.run(handlers.process_unsubscribe_callback(callback))

    callback.answer.assert_awaited_once_with(
        "Не удалось удалить подписку.",
        show_alert=True,
    )
    callback.message.edit_text.assert_not_awaited()


def test_process_navigation_callback_refreshes_status(monkeypatch):
    callback = make_callback("nav_status")
    keyboard = object()

    monkeypatch.setattr(handlers, "build_status_text", lambda: "status text")
    monkeypatch.setattr(handlers, "status_refresh_keyboard", lambda: keyboard)

    asyncio.run(handlers.process_navigation_callback(callback))

    callback.message.edit_text.assert_awaited_once_with(
        "status text",
        reply_markup=keyboard,
        parse_mode="Markdown",
    )
    callback.answer.assert_awaited_once_with("Данные обновлены")


def test_process_navigation_callback_opens_subscribe_menu(monkeypatch):
    callback = make_callback("nav_subscribe")
    keyboard = object()
    edit_or_notify = AsyncMock()

    monkeypatch.setattr(handlers, "build_subscribe_keyboard", lambda user_id: keyboard)
    monkeypatch.setattr(handlers, "edit_or_notify", edit_or_notify)

    asyncio.run(handlers.process_navigation_callback(callback))

    edit_or_notify.assert_awaited_once_with(
        callback,
        "🎯 **Выбери монету для подписки:**",
        keyboard,
    )


def test_process_navigation_callback_shows_all_subscribed_state(monkeypatch):
    callback = make_callback("nav_subscribe")
    edit_or_notify = AsyncMock()

    monkeypatch.setattr(handlers, "build_subscribe_keyboard", lambda user_id: None)
    monkeypatch.setattr(handlers, "edit_or_notify", edit_or_notify)

    asyncio.run(handlers.process_navigation_callback(callback))

    args, _kwargs = edit_or_notify.await_args
    assert args[0] is callback
    assert "подписан на все доступные" in args[1]
    assert args[2] is not None


def test_process_navigation_callback_opens_unsubscribe_menu(monkeypatch):
    callback = make_callback("nav_unsubscribe")
    keyboard = object()
    edit_or_notify = AsyncMock()

    monkeypatch.setattr(
        handlers,
        "build_unsubscribe_view",
        lambda user_id: ("unsubscribe text", keyboard),
    )
    monkeypatch.setattr(handlers, "edit_or_notify", edit_or_notify)

    asyncio.run(handlers.process_navigation_callback(callback))

    edit_or_notify.assert_awaited_once_with(callback, "unsubscribe text", keyboard)


def test_process_navigation_callback_opens_subscriptions_view(monkeypatch):
    callback = make_callback("nav_subscriptions")
    keyboard = object()
    edit_or_notify = AsyncMock()

    monkeypatch.setattr(
        handlers,
        "build_subscriptions_view",
        lambda user_id: ("subscriptions text", keyboard),
    )
    monkeypatch.setattr(handlers, "edit_or_notify", edit_or_notify)

    asyncio.run(handlers.process_navigation_callback(callback))

    edit_or_notify.assert_awaited_once_with(callback, "subscriptions text", keyboard)


def test_process_navigation_callback_opens_main_menu(monkeypatch):
    callback = make_callback("nav_menu")
    edit_or_notify = AsyncMock()

    monkeypatch.setattr(handlers, "edit_or_notify", edit_or_notify)

    asyncio.run(handlers.process_navigation_callback(callback))

    args, _kwargs = edit_or_notify.await_args
    assert args[0] is callback
    assert args[1] == "Главное меню:"
    assert args[2] is not None
