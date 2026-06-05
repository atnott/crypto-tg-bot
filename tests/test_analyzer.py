import pytest

from src.analytics import analyzer


def test_analyze_market_trend_returns_neutral_when_history_is_too_short(monkeypatch):
    monkeypatch.setattr(
        analyzer,
        "get_recent_prices",
        lambda asset_id, limit: [(100.0, "2026-06-04T00:00:00")],
    )

    direction, is_anomaly, description = analyzer.analyze_market_trend(asset_id=1)

    assert direction == "NEUTRAL"
    assert is_anomaly is False
    assert "Недостаточно данных" in description


@pytest.mark.parametrize(
    ("prices", "expected_direction", "expected_is_anomaly", "expected_text"),
    [
        ([100.0, 101.0, 102.0, 103.0, 104.0], "PUMP", True, "взлет"),
        ([104.0, 103.0, 102.0, 101.0, 100.0], "DUMP", True, "падение"),
        ([100.0, 100.0, 100.0, 100.0, 100.0], "STABLE", False, "Цена стабильна"),
    ],
)
def test_analyze_market_trend_classifies_market_scenarios(
    monkeypatch,
    prices,
    expected_direction,
    expected_is_anomaly,
    expected_text,
):
    monkeypatch.setattr(
        analyzer,
        "get_recent_prices",
        lambda asset_id, limit: [
            (price, f"2026-06-04T00:0{index}:00")
            for index, price in enumerate(prices)
        ],
    )

    direction, is_anomaly, description = analyzer.analyze_market_trend(asset_id=1)

    assert direction == expected_direction
    assert is_anomaly is expected_is_anomaly
    assert expected_text in description
