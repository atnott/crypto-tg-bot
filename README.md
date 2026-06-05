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
- **Infrastructure:** Makefile, Docker Compose

## Архитектура

![Схема архитектуры](./images/schema.png)

Проект запускается как два процесса: Telegram-бот обрабатывает пользовательские
команды и подписки, а сборщик получает котировки с Kraken, сохраняет данные в
SQLite и отправляет уведомления при обнаружении аномалий. Подробные диаграммы
архитектуры, сценариев и базы данных находятся в
[docs/architecture.md](./docs/architecture.md).

## Структура проекта

```text
.
├── .env.example
├── Makefile
├── Dockerfile
├── compose.yaml
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── README.md
├── CONTRIBUTING.md
├── LICENSE
├── docs/
│   ├── api.rst
│   ├── architecture.md
│   ├── diagrams/
│   ├── domain.md
│   ├── overview.md
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
└── tests/
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

2. Установите runtime-зависимости:

```bash
make install
```

Для разработки, тестов, сборки документации и публикации пакета используйте:

```bash
make install-dev
```

3. Создайте файл `.env` в корне проекта:

```env
BOT_TOKEN=your_telegram_bot_token
DB_PATH=data/crypto_bot.sqlite
```

`BOT_TOKEN` обязателен для запуска бота и сборщика, потому что сборщик использует объект бота для отправки уведомлений подписчикам. `DB_PATH` можно не задавать: по умолчанию используется `data/crypto_bot.sqlite`.

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

Для запуска обоих процессов в Docker:

```bash
make docker-up
```

Остановить контейнеры и удалить Docker volume можно командой:

```bash
make docker-down
```

## Проверка

Запустить тесты:

```bash
make test
```

Собрать HTML-документацию:

```bash
make docs
```

## Команды Makefile

- `make install` — установить runtime-зависимости.
- `make install-dev` — установить зависимости для разработки, тестов и документации.
- `make init` — создать таблицы базы данных.
- `make seed` — заполнить таблицу `assets`.
- `make bot` — запустить Telegram-бота.
- `make collector` — запустить сборщик котировок.
- `make test` — запустить unit-тесты.
- `make docs` — собрать HTML-документацию Sphinx.
- `make clean` — удалить `__pycache__`.
- `make docker-up` — запустить бота и сборщик в Docker Compose.
- `make docker-down` — остановить Docker Compose и удалить volume с данными.

## Команды Telegram-бота

- `/start` — зарегистрироваться и открыть меню.
- `/status` — посмотреть последние сохранённые цены.
- `/subscribe` — подписаться на уведомления по активу.
- `/unsubscribe` — отписаться от актива.
- `/subscriptions` — посмотреть активные подписки.
- `/help` — открыть справку.

Также бот поддерживает кнопки быстрого доступа: статус рынка, мои подписки, подписка, отписка и помощь.

## Документация

- [Обзор проекта](./docs/overview.md)
- [Предметная область](./docs/domain.md)
- [Архитектура и диаграммы](./docs/architecture.md)
- [API-документация](./docs/api.rst)
- [Как стать участником проекта](./CONTRIBUTING.md)
- [Дневник разработки](./docs/dev_log.md)

## Лицензия

Проект распространяется под лицензией MIT. Подробнее см. [LICENSE](./LICENSE).
