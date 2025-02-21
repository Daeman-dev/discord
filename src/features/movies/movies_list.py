import sqlite3

import discord

from src.main.env_variables import DATABASE_FILE


# Команда для просмотра всех добавленных фильмов

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
