import sqlite3

import pytest

from src.database import db_manager, schema


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    db_path = tmp_path / "crypto_bot.sqlite"
    monkeypatch.setattr(schema, "db_path", str(db_path))
    monkeypatch.setattr(db_manager, "DB_PATH", str(db_path))

    schema.db_init()

    return db_path


@pytest.fixture
def user_id(temp_db):
    user_id = 42
    db_manager.add_user(user_id, "alice", "2026-06-04T00:00:00+00:00")
    return user_id


@pytest.fixture
def asset_id(temp_db):
    return add_test_asset(temp_db)


def add_test_asset(db_path, ticker="BTC/USDT", full_name="Bitcoin"):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO assets (ticker, full_name) VALUES (?, ?)",
            (ticker, full_name),
        )
        return cursor.lastrowid


def test_subscription_lifecycle_uses_assets_and_users(asset_id, user_id):
    assert db_manager.add_subscription(user_id, "btc/usdt") is True
    assert db_manager.get_user_subscriptions(user_id) == ["BTC/USDT"]
    assert db_manager.get_subscribers(asset_id) == [user_id]

    assert db_manager.remove_subscription(user_id, "BTC/USDT") is True
    assert db_manager.get_user_subscriptions(user_id) == []
    assert db_manager.remove_subscription(user_id, "BTC/USDT") is False


def test_price_history_is_saved_and_returned_in_chronological_order(asset_id):
    db_manager.add_price_record(asset_id, 100.0, 10.0, "2026-06-04T00:00:00+00:00")
    db_manager.add_price_record(asset_id, 105.0, 12.0, "2026-06-04T00:01:00+00:00")

    assert db_manager.get_last_price(asset_id) == (
        105.0,
        12.0,
        "2026-06-04T00:01:00+00:00",
    )
    assert db_manager.get_recent_prices(asset_id, limit=2) == [
        (100.0, "2026-06-04T00:00:00+00:00"),
        (105.0, "2026-06-04T00:01:00+00:00"),
    ]


def test_add_subscription_rejects_unknown_ticker(user_id):
    assert db_manager.add_subscription(user_id, "UNKNOWN/USDT") is False
    assert db_manager.get_user_subscriptions(user_id) == []


def test_analytics_and_notifications_are_written_to_database(asset_id, user_id, temp_db):
    db_manager.log_analytics(
        asset_id,
        "PUMP",
        True,
        "Фиксация волатильности",
        "2026-06-04T00:02:00+00:00",
    )
    db_manager.archive_notification(
        user_id,
        "Test alert",
        "2026-06-04T00:03:00+00:00",
    )

    with sqlite3.connect(temp_db) as conn:
        analytics_row = conn.execute(
            "SELECT asset_id, predicted_direction, is_anomaly FROM analytics"
        ).fetchone()
        notification_row = conn.execute(
            "SELECT user_id, message_text FROM notifications_archive"
        ).fetchone()

    assert analytics_row == (asset_id, "PUMP", 1)
    assert notification_row == (user_id, "Test alert")
