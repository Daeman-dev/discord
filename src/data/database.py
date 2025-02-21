import sqlite3

from src.main.env_variables import DATABASE_FILE


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
