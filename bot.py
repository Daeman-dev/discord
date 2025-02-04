import discord
from discord.ext import commands

# Настройка intents (намерений) для бота
intents = discord.Intents.default()
intents.message_content = True  # Включаем доступ к содержимому сообщений

# Создаем экземпляр бота с префиксом команды "!"
bot = commands.Bot(command_prefix="!", intents=intents)

# Список пользователей, которых нужно отмечать
users_to_mention = ["_daeman_"]  # Замените на реальные имена пользователей

# Событие, которое срабатывает при успешном запуске бота
@bot.event
async def on_ready():
    print(f"Бот {bot.user.name} готов к работе!")

# Команда для отметки пользователей
@bot.command(name="упомянуть")
async def mention_users(ctx):
    # Формируем строку с упоминаниями
    mentions = " ".join([f"@{user}" for user in users_to_mention])
    await ctx.send(f"Внимание! {mentions}")

# Запуск бота
bot.run("MTMzNjI3OTEwNzYzNzQ4MTU0Mg.GBhQSq.Zv2O4DQYVcOrCm1UgZJan5EYXyDdvzFybbjOVc")  # Замените "YOUR_BOT_TOKEN" на токен вашего бота
