VENV = .venv
PYTHON = $(VENV)/bin/python

.PHONY: docs test seed collector bot clean init

help:
	@echo "📌 Доступные команды для разработки:"
	@echo "  make init        - Инициализировать схему базы данных"
	@echo "  make seed        - Заполнить БД базовыми монетами (seed)"
	@echo "  make collector   - Запустить сборщик котировок локально"
	@echo "  make bot         - Запустить Telegram-бота локально"
	@echo "  make test        - Запустить unit-тесты (pytest)"
	@echo "  make docs        - Собрать HTML-документацию Sphinx"
	@echo "  make clean       - Очистить кэш компиляции (__pycache__)"
	@echo "  make docker-up   - Запустить всю систему в Docker контейнерах"
	@echo "  make docker-down - Остановить Docker контейнеры и очистить диски"

init:
	$(PYTHON) -m src.database.schema

seed:
	$(PYTHON) -m src.database.seed

collector:
	$(PYTHON) -m src.data_collector.collector

bot:
	$(PYTHON) -m src.bot.bot_main

test:
	$(PYTHON) -m pytest

docs:
	$(PYTHON) -m sphinx -b html docs docs/_build/html

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +

docker-up:
	docker compose up --build

docker-down:
	docker compose down -v
