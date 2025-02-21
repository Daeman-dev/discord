import asyncio
import random
import sqlite3

import discord
from discord import Option

from src.launcher.variables.local import bot, DATABASE_FILE


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