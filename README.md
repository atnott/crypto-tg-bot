# Crypto Telegram Bot

Open-source система для мониторинга аномалий курса криптовалют с уведомлениями в Telegram.

Проект собирает рыночные данные с биржи Kraken через `ccxt`, сохраняет историю цен в SQLite, анализирует краткосрочный тренд и отправляет пользователям Telegram-уведомления по выбранным активам.

## О проекте

Проект разрабатывается в рамках учебных курсов по "Разработке Open Source" и "Информатике". Основная цель — создать автономный инструмент, который помогает трейдерам замечать резкие изменения на рынке без необходимости постоянно следить за графиками.

## Возможности

- сбор актуальных цен и объёмов торгов с Kraken;
- хранение истории котировок в SQLite;
- анализ последних цен по простому алгоритму волатильности и скользящих средних;
- регистрация пользователей Telegram;
- подписка и отписка от отдельных торговых пар;
- отправка алертов при обнаружении аномального изменения цены;
- архивирование отправленных уведомлений;
- быстрые кнопки навигации в Telegram-боте.

## Стек технологий

- **Backend:** Python 3.10+
- **Telegram Bot:** aiogram 3
- **Market Data:** ccxt
- **Database:** SQLite
- **Configuration:** python-dotenv
- **Infrastructure:** Makefile

## Структура проекта

```text
.
├── main.py
├── Makefile
├── requirements.txt
├── README.md
├── docs/
│   └── dev_log.md
├── images/
│   ├── schema.png
│   └── db_schema.png
└── src/
    ├── config.py
    ├── analytics/
    │   └── analyzer.py
    ├── bot/
    │   ├── bot_main.py
    │   ├── handlers.py
    │   ├── keyboards.py
    │   └── messages.py
    ├── data_collector/
    │   └── collector.py
    └── database/
        ├── db_manager.py
        ├── schema.py
        └── seed.py
```

## Основные модули

- `src/config.py` — загрузка `.env`, токена Telegram-бота и пути к базе данных.
- `src/database/schema.py` — создание таблиц SQLite.
- `src/database/seed.py` — заполнение справочника отслеживаемых криптовалют.
- `src/database/db_manager.py` — функции работы с БД.
- `src/data_collector/collector.py` — сбор рыночных данных, запуск анализа и отправка алертов.
- `src/analytics/analyzer.py` — расчёт тренда и определение аномалии.
- `src/bot/bot_main.py` — точка запуска Telegram-бота.
- `src/bot/handlers.py` — команды, кнопки и callback-сценарии.
- `src/bot/keyboards.py` — reply- и inline-клавиатуры.
- `src/bot/messages.py` — тексты сообщений.

## Подготовка окружения

1. Создайте виртуальное окружение:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Установите зависимости:

```bash
pip install -r requirements.txt
```

3. Создайте файл `.env` в корне проекта:

```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_ID=your_telegram_id
```

`BOT_TOKEN` обязателен для запуска бота и сборщика, потому что сборщик использует объект бота для отправки уведомлений подписчикам.

## Запуск

Сначала создайте таблицы и заполните справочник активов:

```bash
make init
make seed
```

Затем запустите Telegram-бота:

```bash
make bot
```

В отдельном терминале запустите сборщик рыночных данных:

```bash
make collector
```

## Команды Makefile

- `make init` — создать таблицы базы данных.
- `make seed` — заполнить таблицу `assets`.
- `make bot` — запустить Telegram-бота.
- `make collector` — запустить сборщик котировок.
- `make clean` — удалить `__pycache__`.

## Команды Telegram-бота

- `/start` — зарегистрироваться и открыть меню.
- `/status` — посмотреть последние сохранённые цены.
- `/subscribe` — подписаться на уведомления по активу.
- `/unsubscribe` — отписаться от актива.
- `/subscriptions` — посмотреть активные подписки.
- `/help` — открыть справку.

Также бот поддерживает кнопки быстрого доступа: статус рынка, мои подписки, подписка, отписка и помощь.

## Документация

Подробный дневник разработки и описание базы данных находятся в [docs/dev_log.md](./docs/dev_log.md).
