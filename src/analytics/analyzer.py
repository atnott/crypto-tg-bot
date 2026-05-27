from src.database.db_manager import get_recent_prices

def check_volatility(asset_id: int) -> tuple[bool, float]:
    rows = get_recent_prices(asset_id, 5)

    if len(rows) < 2:
        return (False, 0.0)

    current_price = rows[-1][0]
    old_price = rows[0][0]

    if old_price == 0:
        return (False, 0.0)

    percent_change = (current_price - old_price) / old_price * 100
    if abs(percent_change) >= 0.5:
        return (True, percent_change)

    return (False, percent_change)

