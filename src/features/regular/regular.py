import asyncio

import schedule

from src.features.birthday.birthday import check_birthdays, remove_birthday_roles
from src.features.daily.regular import send_mentions, send_weekly_statistics


# Задача для выполнения каждый день в определённое время
def schedule_daily_tasks(bot):
    schedule.every().day.at("06:00").do(lambda: asyncio.create_task(send_mentions(bot)))
    schedule.every().day.at("00:00").do(lambda: asyncio.create_task(check_birthdays(bot)))  # Проверка в полночь
    schedule.every().day.at("00:00").do(lambda: asyncio.create_task(remove_birthday_roles(bot)))  # Проверка в полночь
    schedule.every().sunday.at("12:00").do(
        lambda: asyncio.create_task(send_weekly_statistics(bot)))  # Проверка на воскресенье и отправку статистики
