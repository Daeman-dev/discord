import sqlite3
from datetime import datetime

import discord

from src.main.env_variables import DATABASE_FILE


async def wake_up(ctx: discord.ApplicationContext):
    """
    Записывает время пробуждения пользователя в базу данных.
    """
    user_id = ctx.author.id
    wake_up_time = datetime.now().strftime("%H:%M")  # Время в формате "ЧЧ:ММ"
    wake_up_date = datetime.now().strftime("%Y-%m-%d")  # Дата в формате "ГГГГ-ММ-ДД"

    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        # Добавляем запись о времени пробуждения
        cursor.execute("""
            INSERT INTO wake_up_times (user_id, wake_up_time, wake_up_date)
            VALUES (?, ?, ?)
        """, (user_id, wake_up_time, wake_up_date))
        conn.commit()

    await ctx.respond(f"Время пробуждения записано: {wake_up_time}")
