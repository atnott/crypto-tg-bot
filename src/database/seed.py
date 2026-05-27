import sqlite3
from src.config import DB_PATH


def seed_assets():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    volatility_assets = [
        ('BTC/USDT', 'Bitcoin'),
        ('ETH/USDT', 'Ethereum'),
        ('XRP/USDT', 'Ripple'),
        ('SOL/USDT', 'Solana'),
        ('ADA/USDT', 'Cardano'),
        ('DOT/USDT', 'Polkadot'),
        ('DOGE/USDT', 'Dogecoin'),
        ('SHIB/USDT', 'Shiba Inu'),
        ('AVAX/USDT', 'Avalanche'),
        ('LINK/USDT', 'Chainlink'),
        ('LTC/USDT', 'Litecoin'),
        ('NEAR/USD', 'NEAR Protocol'),
        ('UNI/USD', 'Uniswap'),
        ('PEPE/USD', 'Pepe'),
        ('RENDER/USD', 'Render Token'),
        ('WIF/USD', 'dogwifhat'),
        ('BONK/USD', 'Bonk')
        ]

    try:
        cursor.executemany(
            "INSERT OR IGNORE INTO assets (ticker, full_name) VALUES (?, ?);",
            volatility_assets
        )
        conn.commit()
    except Exception as e:
        print(f"❌ Ошибка при наполнении базы данных: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    seed_assets()