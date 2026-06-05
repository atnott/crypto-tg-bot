import asyncio

from src.data_collector import collector


class FakeExchange:
    def __init__(self):
        self.fetch_ticker_calls = []

    def fetch_ticker(self, ticker):
        self.fetch_ticker_calls.append(ticker)
        return {
            "symbol": ticker,
            "last": 105.5,
            "baseVolume": 12.3,
            "datetime": "2026-06-04T00:01:00+00:00",
        }


class FakeBot:
    def __init__(self, failing_chat_ids=None):
        self.failing_chat_ids = set(failing_chat_ids or [])
        self.send_message_calls = []

    async def send_message(self, chat_id, text, parse_mode=None):
        self.send_message_calls.append(
            {
                "chat_id": chat_id,
                "text": text,
                "parse_mode": parse_mode,
            }
        )
        if chat_id in self.failing_chat_ids:
            raise RuntimeError("Telegram delivery failed")


def patch_pipeline_dependencies(monkeypatch, is_anomaly):
    exchange = FakeExchange()
    monkeypatch.setattr(collector, "exchange", exchange)
    monkeypatch.setattr(collector, "add_price_record", lambda *args: None)
    monkeypatch.setattr(
        collector,
        "analyze_market_trend",
        lambda asset_id: ("PUMP", is_anomaly, "Фиксация волатильности"),
    )
    monkeypatch.setattr(collector, "log_analytics", lambda *args: None)
    return exchange


def test_fetch_market_data_sends_and_archives_alerts_for_anomaly(monkeypatch):
    timestamp = "2026-06-04T00:01:00+00:00"
    bot = FakeBot()
    archived_notifications = []

    patch_pipeline_dependencies(monkeypatch, is_anomaly=True)
    monkeypatch.setattr(collector, "bot", bot)
    monkeypatch.setattr(collector, "get_subscribers", lambda asset_id: [42, 84])
    monkeypatch.setattr(
        collector,
        "archive_notification",
        lambda *args: archived_notifications.append(args),
    )

    asyncio.run(collector.fetch_market_data(asset_id=1, ticker="BTC/USDT"))

    assert [call["chat_id"] for call in bot.send_message_calls] == [42, 84]
    assert {call["parse_mode"] for call in bot.send_message_calls} == {"Markdown"}
    assert all("BTC/USDT" in call["text"] for call in bot.send_message_calls)
    assert all("PUMP" in call["text"] for call in bot.send_message_calls)
    assert all("105.5" in call["text"] for call in bot.send_message_calls)
    assert archived_notifications == [
        (42, bot.send_message_calls[0]["text"], timestamp),
        (84, bot.send_message_calls[1]["text"], timestamp),
    ]


def test_fetch_market_data_does_not_send_alert_when_analysis_is_not_anomaly(monkeypatch):
    bot = FakeBot()
    archived_notifications = []

    patch_pipeline_dependencies(monkeypatch, is_anomaly=False)
    monkeypatch.setattr(collector, "bot", bot)
    monkeypatch.setattr(
        collector,
        "get_subscribers",
        lambda asset_id: (_ for _ in ()).throw(AssertionError("unexpected call")),
    )
    monkeypatch.setattr(
        collector,
        "archive_notification",
        lambda *args: archived_notifications.append(args),
    )

    asyncio.run(collector.fetch_market_data(asset_id=1, ticker="BTC/USDT"))

    assert bot.send_message_calls == []
    assert archived_notifications == []


def test_fetch_market_data_continues_after_one_alert_send_fails(monkeypatch, capsys):
    timestamp = "2026-06-04T00:01:00+00:00"
    bot = FakeBot(failing_chat_ids={42})
    archived_notifications = []

    patch_pipeline_dependencies(monkeypatch, is_anomaly=True)
    monkeypatch.setattr(collector, "bot", bot)
    monkeypatch.setattr(collector, "get_subscribers", lambda asset_id: [42, 84])
    monkeypatch.setattr(
        collector,
        "archive_notification",
        lambda *args: archived_notifications.append(args),
    )

    asyncio.run(collector.fetch_market_data(asset_id=1, ticker="BTC/USDT"))

    assert [call["chat_id"] for call in bot.send_message_calls] == [42, 84]
    assert archived_notifications == [(84, bot.send_message_calls[1]["text"], timestamp)]
    assert "Не удалось отправить сообщение пользователю 42" in capsys.readouterr().out
