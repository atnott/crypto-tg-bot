# Crypto Analytics Core

Микро-библиотека для анализа рыночных трендов криптовалют и фиксации аномальной волатильности. 
Использует метод пересечения скользящих средних

## Установка

```bash
pip install crypto-analytics
```

## Использование
```bash
from analytics.analyzer import analyze_market_trend

prices = [100.0, 101.5, 102.3, 101.9, 103.5]
predicted_direction, is_anomaly, description = analyze_market_trend(prices)

print(predicted_direction)  # Выведет: PUMP, DUMP или STABLE
```