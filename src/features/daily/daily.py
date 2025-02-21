import sqlite3
from datetime import datetime, timedelta

import discord

from src.constants import channels_ids, users_ids
from src.launcher.variables.local import bot, DATABASE_FILE

USERS_TO_MENTION = [users_ids.DAEMAN_ID, users_ids.MATE_ID, users_ids.SANI4FOREVER_ID, users_ids.SINTETIK_ID]

async def send_mentions():
    channel = bot.get_channel(channels_ids.COLLOQUIUM_ID)
    if channel:
        mentions = " ".join([f"<@{user_id}>" for user_id in USERS_TO_MENTION])
        await channel.send(f"**Дейлик!** {mentions}")

# Команда для времени просыпания
@bot.slash_command(
    name="япроснулся",
    description="Записать время пробуждения."
)
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

# @bot.slash_command(
#     name="добавитьфильм",
#     description="Добавить фильм в список."
# )
# async def add_movie(
#     ctx: discord.ApplicationContext,
#     title: Option(str, "Название фильма.")
# ):
#     """
#     Добавляет фильм в список не просмотренных.
#     """
#     with sqlite3.connect(DATABASE_FILE) as conn:
#         cursor = conn.cursor()
#         cursor.execute("INSERT INTO movies (title, watched) VALUES (?, 0)", (title,))
#         conn.commit()
#     await ctx.respond(f"Фильм '{title}' добавлен в список!")


# Команда вывода статистики
@bot.slash_command(
    name="статистика",
    description="Показать статистику пробуждений за текущую неделю."
)
async def show_statistics(ctx: discord.ApplicationContext):
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

async def send_weekly_statistics():
    """
    Отправляет статистику пробуждений за неделю.
    """
    channel = bot.get_channel(channels_ids.COLLOQUIUM_ID)  # Канал для отправки статистики
    if not channel:
        print("Канал для статистики не найден!")
        return

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
            await channel.send("На этой неделе ещё никто не просыпался!")
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
        await channel.send(f"**Статистика пробуждений за неделю:**\n{table}")