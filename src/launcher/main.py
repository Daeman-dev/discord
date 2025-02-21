import asyncio

import discord
import schedule

from src.database.database import init_db
from src.features.regular_tasks.regular import schedule_daily_tasks
from src.launcher.variables import local
from src.launcher.variables.local import bot

# BOT_TOKEN = env.BOT_TOKEN
# DATABASE_FILE = env.DATABASE_FILE

BOT_TOKEN = local.BOT_TOKEN
DATABASE_FILE = local.DATABASE_FILE

# Настройка intents (намерений) для бота
intents = discord.Intents.default()
intents.message_content = True  # Включаем доступ к содержимому сообщений
intents.members = True  # Включаем доступ к информации об участниках сервера

# Инициализация базы данных при старте
init_db()

# Событие, которое срабатывает при успешном запуске бота
@bot.event
async def on_ready():
    await bot.sync_commands()  # Синхронизация слэш-команд
    print(f"Бот {bot.user.name} готов к работе!")
    schedule_daily_tasks()  # Запускаем планировщик задач
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)  # Ожидаем 1 секунду перед следующей проверкой

# Запуск бота
bot.run(BOT_TOKEN)