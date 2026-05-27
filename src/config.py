import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = os.getenv('ADMIN_ID')

if not BOT_TOKEN:
    raise ValueError("❌ Критическая ошибка: Переменная окружения BOT_TOKEN не задана в файле .env!")

DB_PATH = str(BASE_DIR / 'data' / 'crypto_bot.sqlite')
