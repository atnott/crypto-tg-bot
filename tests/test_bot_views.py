from src.bot import handlers


def flatten_buttons(markup):
    return [button for row in markup.inline_keyboard for button in row]


def test_build_status_text_returns_empty_assets_message(monkeypatch):
    monkeypatch.setattr(handlers, "get_all_assets", lambda: [])

    assert handlers.build_status_text() == "В базе данных нет отслеживаемых активов"


def test_build_status_text_includes_prices_and_missing_data(monkeypatch):
    monkeypatch.setattr(
        handlers,
        "get_all_assets",
        lambda: [(1, "BTC/USDT"), (2, "ETH/USDT")],
    )
    monkeypatch.setattr(
        handlers,
        "get_last_price",
        lambda asset_id: {
            1: (105.5, 12.3, "2026-06-04T00:01:00+00:00"),
            2: None,
        }[asset_id],
    )

    text = handlers.build_status_text()

    assert "Актуальный статус рынка" in text
    assert "**BTC/USDT**" in text
    assert "Последняя цена: `105.5`" in text
    assert "Объем торгов: `12.3`" in text
    assert "2026-06-04T00:01:00+00:00" in text
    assert "**ETH/USDT**: Данные еще не собраны" in text


def test_build_subscribe_keyboard_omits_existing_subscriptions(monkeypatch):
    monkeypatch.setattr(
        handlers,
        "get_all_assets",
        lambda: [(1, "BTC/USDT"), (2, "ETH/USDT"), (3, "SOL/USDT")],
    )
    monkeypatch.setattr(
        handlers,
        "get_user_subscriptions",
        lambda user_id: ["ETH/USDT"],
    )

    markup = handlers.build_subscribe_keyboard(user_id=42)
    buttons = flatten_buttons(markup)
    button_texts = [button.text for button in buttons]
    callback_data = [button.callback_data for button in buttons]

    assert "➕ BTC/USDT" in button_texts
    assert "➕ SOL/USDT" in button_texts
    assert "➕ ETH/USDT" not in button_texts
    assert "sub_BTC/USDT" in callback_data
    assert "sub_SOL/USDT" in callback_data
    assert "nav_menu" in callback_data


def test_build_subscribe_keyboard_returns_none_when_every_asset_is_subscribed(monkeypatch):
    monkeypatch.setattr(
        handlers,
        "get_all_assets",
        lambda: [(1, "BTC/USDT"), (2, "ETH/USDT")],
    )
    monkeypatch.setattr(
        handlers,
        "get_user_subscriptions",
        lambda user_id: ["BTC/USDT", "ETH/USDT"],
    )

    assert handlers.build_subscribe_keyboard(user_id=42) is None


def test_build_subscriptions_view_returns_empty_state(monkeypatch):
    monkeypatch.setattr(handlers, "get_user_subscriptions", lambda user_id: [])

    text, markup = handlers.build_subscriptions_view(user_id=42)
    callback_data = [button.callback_data for button in flatten_buttons(markup)]

    assert "нет активных подписок" in text
    assert "nav_subscribe" in callback_data
    assert "nav_subscriptions" in callback_data
    assert "nav_unsubscribe" in callback_data
    assert "nav_menu" in callback_data


def test_build_subscriptions_view_lists_active_subscriptions(monkeypatch):
    monkeypatch.setattr(
        handlers,
        "get_user_subscriptions",
        lambda user_id: ["BTC/USDT", "ETH/USDT"],
    )

    text, markup = handlers.build_subscriptions_view(user_id=42)
    callback_data = [button.callback_data for button in flatten_buttons(markup)]

    assert "Твои активные подписки" in text
    assert "`BTC/USDT`" in text
    assert "`ETH/USDT`" in text
    assert "nav_unsubscribe" in callback_data


def test_build_unsubscribe_view_returns_empty_state(monkeypatch):
    monkeypatch.setattr(handlers, "get_user_subscriptions", lambda user_id: [])

    text, markup = handlers.build_unsubscribe_view(user_id=42)
    callback_data = [button.callback_data for button in flatten_buttons(markup)]

    assert "нет активных подписок" in text
    assert callback_data == [
        "nav_status",
        "nav_subscribe",
        "nav_subscriptions",
        "nav_unsubscribe",
    ]


def test_build_unsubscribe_view_lists_active_subscriptions(monkeypatch):
    monkeypatch.setattr(
        handlers,
        "get_user_subscriptions",
        lambda user_id: ["BTC/USDT", "ETH/USDT"],
    )

    text, markup = handlers.build_unsubscribe_view(user_id=42)
    buttons = flatten_buttons(markup)
    button_texts = [button.text for button in buttons]
    callback_data = [button.callback_data for button in buttons]

    assert "Выбери монету" in text
    assert "❌ BTC/USDT" in button_texts
    assert "❌ ETH/USDT" in button_texts
    assert "unsub_BTC/USDT" in callback_data
    assert "unsub_ETH/USDT" in callback_data
    assert "nav_menu" in callback_data
