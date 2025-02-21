import asyncio

import discord
import schedule

from src.data.database import init_db
from src.features import setup_commands
from src.features.regular.regular import schedule_daily_tasks
from src.main import env_variables

intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

setup_commands(bot)

init_db()

# Настройка intents (намерений) для бота
intents = discord.Intents.default()
intents.message_content = True  # Включаем доступ к содержимому сообщений
intents.members = True  # Включаем доступ к информации об участниках сервера


# Событие, которое срабатывает при успешном запуске бота
@bot.event
async def on_ready():
    await bot.sync_commands()  # Синхронизация слэш-команд
    print(f"Бот {bot.user.name} готов к работе!")
    schedule_daily_tasks(bot)  # Запускаем планировщик задач
    while True:
        schedule.run_pending()
        await asyncio.sleep(1)  # Ожидаем 1 секунду перед следующей проверкой


# Запуск бота
bot.run(env_variables.BOT_TOKEN)
