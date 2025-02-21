import sqlite3
from datetime import datetime, timedelta

import discord

from src.main.env_variables import DATABASE_FILE


async def show_statistics(ctx: discord.ApplicationContext, bot):
    """
    Выводит статистику пробуждений за текущую неделю.
    """
    # Получаем начало и конец текущей недели
    today = datetime.now()
    start_of_week = (today - timedelta(days=today.weekday())).strftime("%Y-%m-%d")  # Понедельник
    end_of_week = (today + timedelta(days=6 - today.weekday())).strftime("%Y-%m-%d")  # Воскресенье

    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        # Получаем данные за текущую неделю
        cursor.execute("""
            SELECT user_id, wake_up_time
            FROM wake_up_times
            WHERE wake_up_date BETWEEN ? AND ?
        """, (start_of_week, end_of_week))
        results = cursor.fetchall()

        if not results:
            await ctx.respond("На этой неделе ещё никто не просыпался!")
            return

        # Группируем данные по пользователям
        user_data = {}
        for user_id, wake_up_time in results:
            if user_id not in user_data:
                user_data[user_id] = []
            user_data[user_id].append(wake_up_time)

        # Формируем таблицу
        table = "```\n"
        table += "Имя пользователя | Среднее время | Самое позднее | Самое раннее\n"
        table += "-" * 60 + "\n"

        for user_id, times in user_data.items():
            # Преобразуем время в минуты для вычислений
            times_in_minutes = [int(t.split(":")[0]) * 60 + int(t.split(":")[1]) for t in times]

            # Вычисляем среднее, самое позднее и самое раннее время
            avg_time = sum(times_in_minutes) / len(times_in_minutes)
            latest_time = max(times_in_minutes)
            earliest_time = min(times_in_minutes)

            # Преобразуем минуты обратно в формат "ЧЧ:ММ"
            def minutes_to_time(minutes):
                return f"{int(minutes // 60):02d}:{int(minutes % 60):02d}"

            # Получаем имя пользователя
            user = await bot.fetch_user(user_id)
            username = user.name

            # Добавляем строку в таблицу
            table += f"{username:<16} | {minutes_to_time(avg_time):<13} | {minutes_to_time(latest_time):<14} | {minutes_to_time(earliest_time)}\n"

        table += "```"
        await ctx.respond(table)
