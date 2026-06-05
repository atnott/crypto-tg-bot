import asyncio

from src.data_collector import collector


class FakeExchange:
    def __init__(self, response=None, error=None):
        self.response = response
        self.error = error
        self.fetch_ticker_calls = []

    def fetch_ticker(self, ticker):
        self.fetch_ticker_calls.append(ticker)
        if self.error:
            raise self.error
        return self.response


def test_fetch_market_data_records_price_and_logs_analysis(monkeypatch):
    timestamp = "2026-06-04T00:01:00+00:00"
    exchange = FakeExchange(
        {
            "symbol": "BTC/USDT",
            "last": 105.5,
            "baseVolume": 12.3,
            "datetime": timestamp,
        }
    )
    price_records = []
    analyzed_assets = []
    analytics_records = []

    monkeypatch.setattr(collector, "exchange", exchange)
    monkeypatch.setattr(
        collector,
        "add_price_record",
        lambda *args: price_records.append(args),
    )
    monkeypatch.setattr(
        collector,
        "analyze_market_trend",
        lambda asset_id: analyzed_assets.append(asset_id)
        or ("STABLE", False, "Цена стабильна"),
    )
    monkeypatch.setattr(
        collector,
        "log_analytics",
        lambda *args: analytics_records.append(args),
    )

    asyncio.run(collector.fetch_market_data(asset_id=1, ticker="BTC/USDT"))

    assert exchange.fetch_ticker_calls == ["BTC/USDT"]
    assert price_records == [(1, 105.5, 12.3, timestamp)]
    assert analyzed_assets == [1]
    assert analytics_records == [(1, "STABLE", 0, "Цена стабильна", timestamp)]


def test_fetch_market_data_skips_pipeline_when_exchange_fails(monkeypatch, capsys):
    exchange = FakeExchange(error=RuntimeError("Kraken is unavailable"))
    price_records = []
    analyzed_assets = []
    analytics_records = []

    monkeypatch.setattr(collector, "exchange", exchange)
    monkeypatch.setattr(
        collector,
        "add_price_record",
        lambda *args: price_records.append(args),
    )
    monkeypatch.setattr(
        collector,
        "analyze_market_trend",
        lambda asset_id: analyzed_assets.append(asset_id),
    )
    monkeypatch.setattr(
        collector,
        "log_analytics",
        lambda *args: analytics_records.append(args),
    )

    asyncio.run(collector.fetch_market_data(asset_id=1, ticker="BTC/USDT"))

    assert exchange.fetch_ticker_calls == ["BTC/USDT"]
    assert price_records == []
    assert analyzed_assets == []
    assert analytics_records == []
    assert "Ошибка при сборе BTC/USDT" in capsys.readouterr().out
