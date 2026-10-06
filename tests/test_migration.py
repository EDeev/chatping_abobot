import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import db  # noqa: E402
import migrate_sqlite  # noqa: E402
from conftest import DSN  # noqa: E402


def make_old_dbs(path):
    users = sqlite3.connect(path / "users.db")
    users.executescript("""
        CREATE TABLE users (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL);
        CREATE TABLE "groups" (id INTEGER PRIMARY KEY AUTOINCREMENT, group_id INTEGER NOT NULL);
        INSERT INTO users (user_id) VALUES (111), (222);
        INSERT INTO "groups" (group_id) VALUES (-100), (-200);
    """)
    users.commit()
    base = sqlite3.connect(path / "base.db")
    base.executescript("""
        CREATE TABLE work (group_id INTEGER NOT NULL, state BOOLEAN NOT NULL DEFAULT (True));
        CREATE TABLE stat (group_id INTEGER NOT NULL, mes INTEGER, rep INTEGER, com INTEGER, url INTEGER,
                           med INTEGER, sti INTEGER, voi INTEGER);
        CREATE TABLE edit (user_id INTEGER NOT NULL);
        INSERT INTO work VALUES (1, 1), (2, 0);
        INSERT INTO stat VALUES (1, 50, 5, 1, 0, 2, 3, 4), (2, 7, 0, 0, 0, 0, 0, 0);
        INSERT INTO edit VALUES (2);
    """)
    base.commit()
    groups = sqlite3.connect(path / "groups.db")
    groups.executescript("""
        CREATE TABLE [1] (user_id INTEGER, first_name STRING, mes INTEGER, rep INTEGER, com INTEGER, url INTEGER,
                          med INTEGER, sti INTEGER, voi INTEGER);
        CREATE TABLE [2] (user_id INTEGER, first_name STRING, mes INTEGER, rep INTEGER, com INTEGER, url INTEGER,
                          med INTEGER, sti INTEGER, voi INTEGER);
        INSERT INTO [1] VALUES (1, 'маша', 30, 5, 1, 0, 2, 3, 4), (2, 'котик', 20, 0, 0, 0, 0, 0, 0);
        INSERT INTO [2] VALUES (2, 'котик', 7, 0, 0, 0, 0, 0, 0), (9, 'призрак', 1, 0, 0, 0, 0, 0, 0);
    """)
    groups.commit()


async def test_migration(pool, tmp_path):
    make_old_dbs(tmp_path)
    await db.close()
    assert await migrate_sqlite.migrate(str(tmp_path), DSN, force=True)
    await db.connect(DSN)
    assert await db.pool.fetchval("SELECT short_id FROM chats WHERE id = -200") == 2
    assert await db.get_setting(-200, "events_enabled") is False
    assert (await db.member_stats(-100, 111, "all"))[0] == 30
    assert await db.chat_names(-100) == {"маша": 111, "котик": 222}
    assert await db.pool.fetchval("SELECT custom_name FROM members WHERE chat_id = -100 AND user_id = 222")
    # новый пользователь получает следующий внутренний номер
    await db.ensure_user(333)
    assert await db.pool.fetchval("SELECT short_id FROM users WHERE id = 333") == 3
