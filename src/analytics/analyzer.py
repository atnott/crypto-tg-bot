def analyze_market_trend(prices: list[float]) -> tuple[str, bool, str]:
    """
    Анализирует историю цен, рассчитывает волатильность и тренд.
    Возвращает кортеж: (predicted_direction, is_anomaly, anomaly_description)
    """

    if len(prices) < 2:
        return "NEUTRAL", False, "Недостаточно данных для анализа тренда"

    current_price = prices[-1]
    old_price = prices[0]

    percent_change = ((current_price - old_price) / old_price) * 100
    is_anomaly = False
    anomaly_description = f"Цена стабильна. Изменение: {percent_change:.3f}%"

    if abs(percent_change) >= 0.01:
        is_anomaly = True
        direction_word = "взлет" if percent_change > 0 else "падение"
        anomaly_description = f"Фиксация волатильности: {direction_word} цены на {abs(percent_change):.3f}%."

    ## метод пересечения скользящих средних
    fast_ma = sum(prices[-2:]) / 2 ## быстрая МА (среднее по 2 последним тикам)
    slow_ma = sum(prices) / len(prices) ## медленная МА (среднее по 5)

    if fast_ma > slow_ma:
        predicted_direction = "PUMP"
    elif fast_ma < slow_ma:
        predicted_direction = "DUMP"
    else:
        predicted_direction = "STABLE"

    return predicted_direction, is_anomaly, anomaly_description

