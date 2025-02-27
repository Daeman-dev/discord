import sqlite3
import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.features.daily.wake_up import wake_up
from src.main.env_variables import DATABASE_FILE


@pytest.fixture
def setup_db():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wake_up_times (
            user_id INTEGER,
            wake_up_time TEXT,
            wake_up_date TEXT
        )
    """)
    conn.commit()
    yield conn
    cursor.execute("DROP TABLE wake_up_times")  # Очистка после тестов
    conn.commit()
    conn.close()


@pytest.mark.asyncio
async def test_wake_up(setup_db):
    conn = setup_db
    cursor = conn.cursor()

    ctx = AsyncMock()
    ctx.author = MagicMock()
    ctx.author.id = 123456789

    await wake_up(ctx)

    expected_time = datetime.now().strftime("%H:%M")
    expected_date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute("SELECT user_id, wake_up_time, wake_up_date FROM wake_up_times WHERE user_id = ?", (ctx.author.id,))
    wake_up_record = cursor.fetchone()

    assert wake_up_record is not None, "Время пробуждения не записалось в базу!"
    assert wake_up_record == (ctx.author.id, expected_time, expected_date), "Запись в базе отличается от ожидаемой!"

    ctx.respond.assert_called_with(f"Время пробуждения записано: {expected_time}")
