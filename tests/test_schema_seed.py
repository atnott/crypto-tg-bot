import sqlite3

from src.database import schema, seed


def test_db_init_creates_expected_tables(tmp_path, monkeypatch):
    db_path = tmp_path / "nested" / "crypto_bot.sqlite"
    monkeypatch.setattr(schema, "db_path", str(db_path))

    schema.db_init()

    with sqlite3.connect(db_path) as conn:
        table_names = {
            row[0]
            for row in conn.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
                """
            )
        }

    assert table_names == {
        "assets",
        "price_history",
        "users",
        "subscriptions",
        "analytics",
        "notifications_archive",
    }


def test_seed_assets_is_idempotent(tmp_path, monkeypatch):
    db_path = tmp_path / "crypto_bot.sqlite"
    monkeypatch.setattr(schema, "db_path", str(db_path))
    monkeypatch.setattr(seed, "DB_PATH", str(db_path))
    schema.db_init()

    seed.seed_assets()
    seed.seed_assets()

    with sqlite3.connect(db_path) as conn:
        asset_count, unique_ticker_count = conn.execute(
            "SELECT COUNT(*), COUNT(DISTINCT ticker) FROM assets"
        ).fetchone()
        sample_assets = conn.execute(
            """
            SELECT ticker, full_name
            FROM assets
            WHERE ticker IN ('BTC/USDT', 'ETH/USDT', 'BONK/USD')
            ORDER BY ticker
            """
        ).fetchall()

    assert asset_count == 17
    assert unique_ticker_count == asset_count
    assert sample_assets == [
        ("BONK/USD", "Bonk"),
        ("BTC/USDT", "Bitcoin"),
        ("ETH/USDT", "Ethereum"),
    ]
