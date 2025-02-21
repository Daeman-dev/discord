import os

BOT_TOKEN = os.getenv("BOT_TOKEN")

DATABASE_FILE = os.getenv("DATABASE_FILE", "data/bot_database.db")  # Путь к файлу базы данных