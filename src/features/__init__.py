import discord
from discord import Option

from src.features.daily.show_stats import show_statistics
from src.features.daily.wake_up import wake_up
from src.features.movies.add_movie import add_movie
from src.features.movies.movies_list import list_all_movies
from src.features.movies.random_movie import random_movie
from src.features.movies.watched_movies import list_watched_movies


def setup_commands(bot):
    #   MOVIES
    @bot.slash_command(name="добавитьфильм", description="Добавить фильм в список.")
    async def init_add_movie(ctx: discord.ApplicationContext, title: Option(str, "Название фильма.")):
        await add_movie(ctx, title)

    @bot.slash_command(name="всефильмы", description="Показать все добавленные фильмы.")
    async def init_movies_list(ctx: discord.ApplicationContext):
        await list_all_movies(ctx)

    @bot.slash_command(name="случайныйфильм", description="Выбрать случайный фильм из списка.")
    async def init_random_movie(ctx: discord.ApplicationContext):
        await random_movie(ctx, bot)

    @bot.slash_command(name="просмотренные", description="Показать все просмотренные фильмы.")
    async def init_list_watched_movies(ctx: discord.ApplicationContext):
        await list_watched_movies(ctx)

    #   DAILY
    @bot.slash_command(name="япроснулся", description="Записать время пробуждения.")
    async def init_wake_up(ctx: discord.ApplicationContext):
        await wake_up(ctx)

    @bot.slash_command(name="статистика", description="Показать статистику пробуждений за текущую неделю.")
    async def init_show_statistics(ctx: discord.ApplicationContext):
        await show_statistics(ctx, bot)
