VENV = .venv
PYTHON = $(VENV)/bin/python

help:
	@echo "Доступные команды для разработки:"
	@echo "  make test       - Запустить unit-тесты"
	@echo "  make seed       - Запустить сидзер базы данных (наполнение assets)"
	@echo "  make collector  - Запустить асинхронный сборщик маркет-даты"
	@echo "  make bot        - Запустить Telegram-бота"
	@echo "  make docs       - Собрать HTML-документацию Sphinx"
	@echo "  make clean      - Очистить кэш компиляции Python (__pycache__)"
	@echo "  make init       - Создание таблиц"

test:
	$(PYTHON) -m pytest

seed:
	$(PYTHON) -m src.database.seed

collector:
	$(PYTHON) -m src.data_collector.collector

bot:
	$(PYTHON) -m src.bot.bot_main

docs:
	$(PYTHON) -m sphinx -b html docs docs/_build/html

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +

init:
	$(PYTHON) -m src.database.schema
