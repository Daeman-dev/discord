import os

# cmd -> setx BOT_TOKEN XXXXXXXX.XXXX.XXXXXX -> relaunch IDE
BOT_TOKEN = os.getenv("BOT_TOKEN")

# cmd -> setx DATABASE_FILE C:\Users\user_name\PycharmProjects\discord\src\data\database.db -> relaunch IDE
DATABASE_FILE = os.getenv("DATABASE_FILE")
