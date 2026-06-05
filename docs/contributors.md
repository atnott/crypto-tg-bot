# Как стать участником проекта

Эта страница помогает быстро подключиться к разработке Crypto Telegram Bot.

## Что можно улучшать

В проект можно вносить:

* исправления ошибок;
* новые тесты;
* улучшения Telegram-бота;
* доработки аналитики;
* документацию и диаграммы;
* улучшения Makefile, Docker и окружения.

## Подготовка окружения

Создайте виртуальное окружение и установите зависимости:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

Для запуска бота нужен файл `.env`:

```text
BOT_TOKEN=your_telegram_bot_token
ADMIN_ID=your_telegram_id
```

Файл `.env`, локальные базы данных и кэши нельзя добавлять в Git.

## Работа над задачей

Выберите небольшую задачу и создайте отдельную ветку:

```text
docs/update-architecture
feature/add-alert-settings
fix/subscription-callback
test/analytics-edge-cases
```

Один коммит должен описывать одно логическое изменение. Хорошие сообщения:

```text
docs: add contributor guide
test: add analytics edge case tests
fix: handle missing market timestamp
build: add documentation build command
```

## Проверка изменений

Перед Pull Request запустите:

```bash
make test
make docs
```

Если менялась база данных:

```bash
make init
make seed
```

Если менялся Docker:

```bash
make docker-up
make docker-down
```

## Pull Request

В Pull Request коротко укажите:

* что изменилось;
* зачем это было сделано;

Пример:

```text
Что изменилось:
- добавлена страница для участников проекта;
- страница подключена в Sphinx.
```

## Перед отправкой

Проверьте, что:

* изменение относится к выбранной задаче;
* тесты и документация запускаются;
* новые страницы подключены в `docs/index.rst`;
* в Git нет `.env`, локальной базы данных и временных файлов.
