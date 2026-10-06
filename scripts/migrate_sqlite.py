"""Перенос данных AboBot из четырёх баз SQLite в PostgreSQL.

    python scripts/migrate_sqlite.py --sqlite-dir /path/to/db --dsn postgresql://…

Старые базы: users.db (users, groups — внутренние номера ↔ id Telegram), base.db (work, stat, edit),
groups.db (таблица на каждый чат со статистикой участников), month.db (месячная статистика).
Месячная статистика не переносится: в старой версии она ни разу не обнулялась и фактически
дублировала статистику за всё время; новая копится по месяцам с момента переноса.
"""
import argparse
import asyncio
import os
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "code"))

import db  # noqa: E402

FIELDS = db.STAT_FIELDS


async def migrate(sqlite_dir, dsn, force=False):
    users_db = sqlite3.connect(os.path.join(sqlite_dir, "users.db"))
    base_db = sqlite3.connect(os.path.join(sqlite_dir, "base.db"))
    groups_db = sqlite3.connect(os.path.join(sqlite_dir, "groups.db"))

    pool = await db.connect(dsn)
    async with pool.acquire() as conn:
        if await conn.fetchval("SELECT count(*) FROM chats"):
            if not force:
                raise SystemExit("В PostgreSQL уже есть данные — перенос остановлен (--force очистит таблицы)")
            await conn.execute("TRUNCATE chats, users, members, chat_stats, member_stats, bot_status_history "
                               "RESTART IDENTITY CASCADE")

        async with conn.transaction():
            # пользователи и чаты с прежними внутренними номерами
            users = {}
            for short, tg in users_db.execute("SELECT id, user_id FROM users ORDER BY id"):
                if tg not in users.values():
                    users[short] = tg
            await conn.executemany("INSERT INTO users (id, short_id) VALUES ($1, $2) ON CONFLICT DO NOTHING",
                                   [(tg, short) for short, tg in users.items()])

            states = dict(base_db.execute("SELECT group_id, state FROM work"))
            chats = {}
            for short, tg in users_db.execute('SELECT id, group_id FROM "groups" ORDER BY id'):
                if tg not in chats.values():
                    chats[short] = tg
            await conn.executemany(
                "INSERT INTO chats (id, short_id, events_enabled) VALUES ($1, $2, $3) ON CONFLICT DO NOTHING",
                [(tg, short, bool(states.get(short, True))) for short, tg in chats.items()])
            for table in ("users", "chats"):
                await conn.execute(f"SELECT setval(pg_get_serial_sequence('{table}', 'short_id'), "
                                   f"GREATEST((SELECT max(short_id) FROM {table}), 1))")

            # статистика чатов за всё время
            chat_rows = []
            for row in base_db.execute(f"SELECT group_id, {', '.join(FIELDS)} FROM stat"):
                if row[0] in chats:
                    chat_rows.append((chats[row[0]], *[v or 0 for v in row[1:]]))
            await conn.executemany(
                f"INSERT INTO chat_stats (chat_id, period, {', '.join(FIELDS)}) "
                f"VALUES ($1, 'all', {', '.join(f'${i}' for i in range(2, 9))}) ON CONFLICT DO NOTHING", chat_rows)

            # участники и их статистика: таблица groups.db на каждый чат
            custom = {r[0] for r in base_db.execute("SELECT user_id FROM edit")}
            tables = [r[0] for r in groups_db.execute("SELECT name FROM sqlite_master WHERE type = 'table'")]
            members, stats, skipped = {}, {}, 0
            for table in tables:
                if not table.lstrip("-").isdigit() or int(table) not in chats:
                    continue
                chat_id = chats[int(table)]
                for row in groups_db.execute(f"SELECT user_id, first_name, {', '.join(FIELDS)} FROM [{table}]"):
                    # SQLite хранит тип по значению: имя «69» лежит числом
                    user_short, name = row[0], "" if row[1] is None else str(row[1])
                    if user_short not in users:
                        skipped += 1
                        continue
                    key = (chat_id, users[user_short])
                    members.setdefault(key, (name, user_short in custom))
                    old = stats.get(key, (0,) * len(FIELDS))
                    stats[key] = tuple(a + (b or 0) for a, b in zip(old, row[2:], strict=True))
            await conn.executemany("INSERT INTO members (chat_id, user_id, name, custom_name) VALUES ($1, $2, $3, $4)",
                                   [(c, u, n, cu) for (c, u), (n, cu) in members.items()])
            await conn.executemany(
                f"INSERT INTO member_stats (chat_id, user_id, period, {', '.join(FIELDS)}) "
                f"VALUES ($1, $2, 'all', {', '.join(f'${i}' for i in range(3, 10))})",
                [(c, u, *s) for (c, u), s in stats.items()])

        report = {
            "users": (len(users), await conn.fetchval("SELECT count(*) FROM users")),
            "chats": (len(chats), await conn.fetchval("SELECT count(*) FROM chats")),
            "members": (len(members), await conn.fetchval("SELECT count(*) FROM members")),
            "chat messages": (sum(r[1] for r in chat_rows),
                              await conn.fetchval("SELECT coalesce(sum(mes), 0) FROM chat_stats WHERE period = 'all'")),
            "member messages": (sum(s[0] for s in stats.values()),
                                await conn.fetchval("SELECT coalesce(sum(mes), 0) FROM member_stats WHERE period = 'all'")),
        }
    await db.close()

    ok = all(a == b for a, b in report.values())
    for key, (src, dst) in report.items():
        print(f"{key:16} SQLite {src:>9}  PostgreSQL {dst:>9}  {'ok' if src == dst else 'MISMATCH'}")
    print(f"участников без пользователя в users.db (пропущено): {skipped}")
    return ok


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--sqlite-dir", required=True)
    parser.add_argument("--dsn", default=os.getenv("DATABASE_URL"))
    parser.add_argument("--force", action="store_true", help="очистить таблицы PostgreSQL перед переносом")
    args = parser.parse_args()
    sys.exit(0 if asyncio.run(migrate(args.sqlite_dir, args.dsn, args.force)) else 1)


if __name__ == "__main__":
    main()
