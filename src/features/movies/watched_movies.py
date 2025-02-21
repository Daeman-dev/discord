import sqlite3

import discord

from src.main.env_variables import DATABASE_FILE


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
