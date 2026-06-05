"""Вспомогательные функции анализа рынка для пакета ``crypto-analytics``.

Модуль содержит чистую вычислительную логику: принимает историю цен и
возвращает классификацию тренда без обращения к Telegram, Kraken или SQLite.
"""


def analyze_market_trend(prices: list[float]) -> tuple[str, bool, str]:
    """Анализирует историю цен и классифицирует краткосрочное движение рынка.

    Функция сравнивает первую и последнюю цены, чтобы оценить волатильность,
    и использует простое пересечение скользящих средних для определения
    направления тренда. Быстрая скользящая средняя считается по двум последним
    ценам, медленная — по всей переданной истории.

    Args:
        prices: История цен от старой к новой. Первая цена используется как
            базовое значение для расчёта процентного изменения, поэтому она не
            должна быть равна нулю.

    Returns:
        Кортеж ``(predicted_direction, is_anomaly, anomaly_description)``:

        * ``predicted_direction`` — одно из значений ``PUMP``, ``DUMP``, ``STABLE`` или ``NEUTRAL``.
        * ``is_anomaly`` — ``True``, если абсолютное изменение цены не меньше ``0.01%``.
        * ``anomaly_description`` — человекочитаемое описание результата анализа.

    Raises:
        ZeroDivisionError: Возникает, если первая цена в ``prices`` равна ``0``.
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
