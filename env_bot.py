import discord
from discord import Option
import schedule
import asyncio
from datetime import datetime, timedelta
import sqlite3
import random
import os

# Загрузка переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
BIRTHDAY_ROLE_ID = int(os.getenv("BIRTHDAY_ROLE_ID", "998877665544332211"))  # ID роли "День рождения"
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "706224150704029697"))  # ID канала для упоминаний
USERS_TO_MENTION = [int(user_id) for user_id in os.getenv("USERS_TO_MENTION", "294860783811035136,294881060263821312,135024441884278784,904383863806128189").split(",")]  # Список ID пользователей
DATABASE_FILE = os.getenv("DATABASE_FILE", "data/bot_database.db")  # Путь к файлу базы данных

# Настройка intents (намерений) для бота
intents = discord.Intents.default()
intents.message_content = True  # Включаем доступ к содержимому сообщений
intents.members = True  # Включаем доступ к информации о участниках сервера

# Создаем экземпляр бота
bot = discord.Bot(intents=intents)

def init_db():
    """Инициализация базы данных и создание таблиц, если они не существуют."""
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        # Таблица для дней рождения
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS birthdays (
                user_id INTEGER PRIMARY KEY,
                birthday TEXT NOT NULL
            )
        """)
        # Таблица для фильмов
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS movies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                watched INTEGER DEFAULT 0
            )
        """)
         # Таблица для времени пробуждения
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wake_up_times (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                wake_up_time TEXT NOT NULL, 
                wake_up_date TEXT NOT NULL   
            )
        """)
        conn.commit()

# Инициализация базы данных при старте
init_db()

# Словарь для отслеживания, когда роль была выдана
role_assignments = {}

# Функция для отправки упоминаний
async def send_mentions():
    channel = bot.get_channel(CHANNEL_ID)
    if channel:
        mentions = " ".join([f"<@{user_id}>" for user_id in USERS_TO_MENTION])
        await channel.send(f"**Дейлик!** {mentions}")

# Функция для проверки дней рождения и выдачи роли
async def check_birthdays():
    today = datetime.now().strftime("%m-%d")  # Получаем текущую дату в формате "MM-DD"
    guild = bot.guilds[0]  # Предполагаем, что бот находится на одном сервере

    # Получаем объект роли "День рождения"
    birthday_role = guild.get_role(BIRTHDAY_ROLE_ID)
    if not birthday_role:
        print("Роль 'День рождения' не найдена!")
        return

    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM birthdays WHERE birthday = ?", (today,))
        users = cursor.fetchall()

        for user_id in users:
            user = guild.get_member(int(user_id[0]))  # Преобразуем user_id в int
            if user:
                # Выдаем роль
                await user.add_roles(birthday_role)
                print(f"Роль 'День рождения' выдана пользователю {user.name}!")
                # Записываем дату выдачи роли
                role_assignments[user_id[0]] = datetime.now().strftime("%Y-%m-%d")
            else:
                print(f"Пользователь с ID {user_id[0]} не найден на сервере.")

# Функция для снятия роли через 5 дней
async def remove_birthday_roles():
    guild = bot.guilds[0]  # Предполагаем, что бот находится на одном сервере
    birthday_role = guild.get_role(BIRTHDAY_ROLE_ID)
    if not birthday_role:
        print("Роль 'День рождения' не найдена!")
        return

    for user_id, assignment_date in list(role_assignments.items()):
        assignment_date = datetime.strptime(assignment_date, "%Y-%m-%d")
        if datetime.now() - assignment_date >= timedelta(days=5):
            user = guild.get_member(int(user_id))  # Преобразуем user_id в int
            if user:
                # Снимаем роль
                await user.remove_roles(birthday_role)
                print(f"Роль 'День рождения' снята у пользователя {user.name}!")
                # Удаляем запись о выдаче роли
                del role_assignments[user_id]
            else:
                print(f"Пользователь с ID {user_id} не найден на сервере.")

# Команда для добавления фильма
@bot.slash_command(
    name="добавитьфильм",
    description="Добавить фильм в список."
)
async def add_movie(
    ctx: discord.ApplicationContext,
    title: Option(str, "Название фильма.")
):
    """
    Добавляет фильм в список не просмотренных.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO movies (title, watched) VALUES (?, 0)", (title,))
        conn.commit()
    await ctx.respond(f"Фильм '{title}' добавлен в список!")

# Команда для выбора случайного фильма
@bot.slash_command(
    name="случайныйфильм",
    description="Выбрать случайный фильм из списка."
)
async def random_movie(ctx: discord.ApplicationContext):
    """
    Выбирает случайный фильм из списка не просмотренных.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM movies WHERE watched = 0")
        movies = cursor.fetchall()

        if not movies:
            await ctx.respond("Список фильмов пуст! Добавьте фильмы с помощью команды `/добавитьфильм`.")
            return

        # Выбираем случайный фильм
        movie_id, movie_title = random.choice(movies)
        await ctx.respond(f"Случайный фильм: **{movie_title}**\nВыберите действие: 👍 (смотреть) или 👎 (отложить).")

        # Добавляем реакции для выбора
        message = await ctx.send("Что вы хотите сделать?")
        await message.add_reaction("👍")  # Смотреть
        await message.add_reaction("👎")  # Отложить

        # Ожидаем реакцию пользователя
        def check(reaction, user):
            return user == ctx.author and str(reaction.emoji) in ["👍", "👎"]

        try:
            reaction, user = await bot.wait_for("reaction_add", timeout=30.0, check=check)

            if str(reaction.emoji) == "👍":
                # Помечаем фильм как просмотренный
                cursor.execute("UPDATE movies SET watched = 1 WHERE id = ?", (movie_id,))
                conn.commit()
                await ctx.send(f"Фильм '{movie_title}' перемещён в список просмотренных!")
            else:
                await ctx.send(f"Фильм '{movie_title}' отложен.")
        except asyncio.TimeoutError:
            await ctx.send("Время вышло! Фильм остаётся в списке.")

# Команда для просмотра всех добавленных фильмов
@bot.slash_command(
    name="всефильмы",
    description="Показать все добавленные фильмы."
)
async def list_all_movies(ctx: discord.ApplicationContext):
    """
    Показывает все фильмы из базы данных.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title, watched FROM movies")
        movies = cursor.fetchall()

        if not movies:
            await ctx.respond("Список фильмов пуст! Добавьте фильмы с помощью команды `/добавитьфильм`.")
            return

        # Формируем сообщение со всеми фильмами
        message = "**Все фильмы:**\n"
        message += "**Не просмотренные:**\n"
        message += "\n".join([title for title, watched in movies if watched == 0]) or "Нет фильмов.\n"
        message += "\n**Просмотренные:**\n"
        message += "\n".join([title for title, watched in movies if watched == 1]) or "Нет фильмов."

        await ctx.respond(message)

# Команда для просмотра просмотренных фильмов
@bot.slash_command(
    name="просмотренные",
    description="Показать все просмотренные фильмы."
)
async def list_watched_movies(ctx: discord.ApplicationContext):
    """
    Показывает все просмотренные фильмы.
    """
    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT title FROM movies WHERE watched = 1")
        movies = cursor.fetchall()

        if not movies:
            await ctx.respond("Список просмотренных фильмов пуст!")
            return

        message = "**Просмотренные фильмы:**\n"
        message += "\n".join([title for title, in movies])
        await ctx.respond(message)
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
    channel = bot.get_channel(CHANNEL_ID)  # Канал для отправки статистики
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

# Задача для выполнения каждый день в определённое время
def schedule_daily_tasks():
    # Укажите время в формате "HH:MM" (например, "09:00")
    schedule.every().day.at("06:00").do(lambda: asyncio.create_task(send_mentions()))
    schedule.every().day.at("00:00").do(lambda: asyncio.create_task(check_birthdays()))  # Проверка в полночь
    schedule.every().day.at("00:00").do(lambda: asyncio.create_task(remove_birthday_roles()))  # Проверка в полночь
    schedule.every().sunday.at("12:00").do(lambda: asyncio.create_task(send_weekly_statistics())) # Проверка на воскресенье и отправку статистики

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