import asyncio
import random
import sqlite3

import discord

from src.main.env_variables import DATABASE_FILE


async def random_movie(ctx: discord.ApplicationContext, bot):
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
