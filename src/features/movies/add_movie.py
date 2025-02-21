import sqlite3

import discord
from discord import Option

from src.main.env_variables import DATABASE_FILE


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
