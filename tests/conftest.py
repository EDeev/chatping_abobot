import os
import sys

import asyncpg
import pytest

os.environ.setdefault("BOT_TOKEN", "123456:TEST")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import db  # noqa: E402

DSN = os.environ.get("TEST_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/abobot_test")


@pytest.fixture
async def pool():
    """Чистая схема на каждый тест"""
    conn = await asyncpg.connect(DSN)
    await conn.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
    await conn.close()
    p = await db.connect(DSN)
    yield p
    await db.close()


class FakeBot:
    """Минимум Bot API для обработчиков: размер чата и права"""

    def __init__(self, size=10, admins=()):
        self.size, self.admins, self.id = size, set(admins), 999

    async def get_chat_member_count(self, chat_id):
        return self.size

    async def get_chat_member(self, chat_id, user_id):
        from types import SimpleNamespace
        return SimpleNamespace(status="administrator" if user_id in self.admins else "member")


@pytest.fixture
def fake_bot():
    return FakeBot
