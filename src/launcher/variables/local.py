import discord

BOT_TOKEN = "MTMzNjI3OTEwNzYzNzQ4MTU0Mg.GBhQSq.Zv2O4DQYVcOrCm1UgZJan5EYXyDdvzFybbjOVc" #K4AY
# BOT_TOKEN = "NzM4NzIyMzMyNDIzNDg3NTk5.G21j5l.U9LDYQT6dKdHeL12PJ8StcVuJfQCeYFw6Q2JGA" #Pazik

DATABASE_FILE = "bot_database.db"

# Настройка intents (намерений) для бота
intents = discord.Intents.default()

# Создаем экземпляр бота
bot = discord.Bot(intents=intents)