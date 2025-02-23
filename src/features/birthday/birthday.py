import os
import sqlite3
from datetime import datetime, timedelta

from src.constants.roles_ids import BIRTHDAY_ROLE_ID
from src.main.env_variables import DATABASE_FILE

# Словарь для отслеживания, когда роль была выдана
role_assignments = {}

BIRTHDAY_ROLE_ID = BIRTHDAY_ROLE_ID

# Функция для проверки дней рождения и выдачи роли
async def check_birthdays(bot):
    today = datetime.now().strftime("%m-%d")  # Получаем текущую дату в формате "MM-DD"
    guild = bot.guilds[0]  # Предполагаем, что бот находится на одном сервере

    # Получаем объект роли "День рождения"
    birthday_role = guild.get_role(BIRTHDAY_ROLE_ID)
    if not birthday_role:
        print("Роль 'День рождения' не найдена!")
        return

    with sqlite3.connect(DATABASE_FILE) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM birthdays WHERE birthday = ?", (today,))
        users = cursor.fetchall()

        for user_id in users:
            user = guild.get_member(int(user_id[0]))  # Преобразуем user_id в int
            if user:
                # Выдаем роль
                await user.add_roles(birthday_role)
                print(f"Роль 'День рождения' выдана пользователю {user.name}!")
                # Записываем дату выдачи роли
                role_assignments[user_id[0]] = datetime.now().strftime("%Y-%m-%d")
            else:
                print(f"Пользователь с ID {user_id[0]} не найден на сервере.")


# Функция для снятия роли через 5 дней
async def remove_birthday_roles(bot):
    guild = bot.guilds[0]  # Предполагаем, что бот находится на одном сервере
    birthday_role = guild.get_role(BIRTHDAY_ROLE_ID)
    if not birthday_role:
        print("Роль 'День рождения' не найдена!")
        return

    for user_id, assignment_date in list(role_assignments.items()):
        assignment_date = datetime.strptime(assignment_date, "%Y-%m-%d")
        if datetime.now() - assignment_date >= timedelta(days=5):
            user = guild.get_member(int(user_id))  # Преобразуем user_id в int
            if user:
                # Снимаем роль
                await user.remove_roles(birthday_role)
                print(f"Роль 'День рождения' снята у пользователя {user.name}!")
                # Удаляем запись о выдаче роли
                del role_assignments[user_id]
            else:
                print(f"Пользователь с ID {user_id} не найден на сервере.")
