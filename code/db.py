"""Работа с PostgreSQL. Счётчики увеличиваются одним запросом (INSERT … ON CONFLICT DO UPDATE)"""
import json
import os
from datetime import date

import asyncpg

COLUMNS = {1: "mes", 2: "rep", 3: "com", 4: "url", 5: "med", 6: "sti", 7: "voi"}
STAT_FIELDS = ("mes", "rep", "com", "url", "med", "sti", "voi")
SETTINGS = ("events_enabled", "mentions_enabled", "voice_names", "delete_service")

pool: asyncpg.Pool | None = None


def month_key(day=None):
    return (day or date.today()).strftime("%Y-%m")


async def connect(dsn):
    global pool
    pool = await asyncpg.create_pool(dsn, min_size=1, max_size=5)
    with open(os.path.join(os.path.dirname(__file__), "schema.sql"), encoding="utf-8") as f:
        await pool.execute(f.read())
    return pool


async def close():
    if pool:
        await pool.close()


# ЧАТЫ И УЧАСТНИКИ
async def ensure_chat(chat_id, title=None):
    await pool.execute(
        "INSERT INTO chats (id, title) VALUES ($1, $2) "
        "ON CONFLICT (id) DO UPDATE SET title = COALESCE(EXCLUDED.title, chats.title)", chat_id, title)


async def chat_exists(chat_id):
    return await pool.fetchval("SELECT EXISTS (SELECT 1 FROM chats WHERE id = $1)", chat_id)


async def migrate_chat(old_id, new_id):
    """Группа стала супергруппой — у неё новый id; связанные таблицы обновятся каскадом"""
    await pool.execute("UPDATE chats SET id = $2 WHERE id = $1 AND NOT EXISTS (SELECT 1 FROM chats WHERE id = $2)",
                       old_id, new_id)


async def ensure_user(user_id):
    await pool.execute("INSERT INTO users (id) VALUES ($1) ON CONFLICT DO NOTHING", user_id)


async def get_setting(chat_id, name):
    assert name in SETTINGS
    value = await pool.fetchval(f"SELECT {name} FROM chats WHERE id = $1", chat_id)
    return True if value is None else value


async def toggle_setting(chat_id, name):
    assert name in SETTINGS
    return await pool.fetchval(f"UPDATE chats SET {name} = NOT {name} WHERE id = $1 RETURNING {name}", chat_id)


async def settings(chat_id):
    row = await pool.fetchrow(f"SELECT {', '.join(SETTINGS)} FROM chats WHERE id = $1", chat_id)
    return dict(row) if row else dict.fromkeys(SETTINGS, True)


async def chat_names(chat_id):
    """Имена действующих участников: {имя: id}"""
    rows = await pool.fetch("SELECT name, user_id FROM members WHERE chat_id = $1 AND left_at IS NULL AND name <> ''",
                            chat_id)
    return {r["name"]: r["user_id"] for r in rows}


async def active_members(chat_id, days=None):
    """Действующие участники: [(id, имя)]; days — только писавшие за последние N дней"""
    query = "SELECT user_id, name FROM members WHERE chat_id = $1 AND left_at IS NULL AND name <> ''"
    args = [chat_id]
    if days:
        query += " AND last_message_at > now() - make_interval(days => $2)"
        args.append(days)
    return [(r["user_id"], r["name"]) for r in await pool.fetch(query + " ORDER BY name", *args)]


async def member_count(chat_id):
    return await pool.fetchval("SELECT count(*) FROM members WHERE chat_id = $1 AND left_at IS NULL", chat_id)


async def member_name(chat_id, user_id):
    return await pool.fetchval("SELECT name FROM members WHERE chat_id = $1 AND user_id = $2", chat_id, user_id)


async def set_custom_name(chat_id, user_id, name):
    await pool.execute("UPDATE members SET name = $3, custom_name = TRUE WHERE chat_id = $1 AND user_id = $2",
                       chat_id, user_id, name)


async def reset_custom_name(chat_id, user_id, name):
    """Возвращает True, если своё имя было задано"""
    return await pool.fetchval(
        "UPDATE members SET name = $3, custom_name = FALSE WHERE chat_id = $1 AND user_id = $2 AND custom_name "
        "RETURNING TRUE", chat_id, user_id, name) or False


async def member_left(chat_id, user_id):
    await pool.execute("UPDATE members SET left_at = now() WHERE chat_id = $1 AND user_id = $2", chat_id, user_id)


async def mark_all(chat_id):
    await pool.execute("UPDATE chats SET last_all_at = now() WHERE id = $1", chat_id)


async def last_all(chat_id):
    return await pool.fetchval("SELECT last_all_at FROM chats WHERE id = $1", chat_id)


# СТАТИСТИКА
async def count(chat_id, user_id, var_ids, name, title=None, day=None):
    """Учёт события: участник появляется в чате (имя обновляется, если не задано своё),
    счётчики var_ids растут за всё время и за текущий месяц — одной транзакцией"""
    periods = ("all", month_key(day))
    columns = [COLUMNS[v] for v in var_ids]
    increments = ", ".join(f"{c} = s.{c} + EXCLUDED.{c}" for c in columns)
    values = ", ".join("1" for _ in columns)
    column_list = ", ".join(columns)

    async with pool.acquire() as conn, conn.transaction():
        await conn.execute(
            "INSERT INTO chats (id, title) VALUES ($1, $2) "
            "ON CONFLICT (id) DO UPDATE SET title = COALESCE(EXCLUDED.title, chats.title)", chat_id, title)
        await conn.execute("INSERT INTO users (id) VALUES ($1) ON CONFLICT DO NOTHING", user_id)
        await conn.execute(
            "INSERT INTO members (chat_id, user_id, name, last_message_at) VALUES ($1, $2, $3, now()) "
            "ON CONFLICT (chat_id, user_id) DO UPDATE SET last_message_at = now(), left_at = NULL, "
            "name = CASE WHEN members.custom_name THEN members.name ELSE EXCLUDED.name END",
            chat_id, user_id, name)
        for period in periods:
            await conn.execute(
                f"INSERT INTO chat_stats AS s (chat_id, period, {column_list}) VALUES ($1, $2, {values}) "
                f"ON CONFLICT (chat_id, period) DO UPDATE SET {increments}", chat_id, period)
            await conn.execute(
                f"INSERT INTO member_stats AS s (chat_id, user_id, period, {column_list}) VALUES ($1, $2, $3, {values}) "
                f"ON CONFLICT (chat_id, user_id, period) DO UPDATE SET {increments}", chat_id, user_id, period)


def _stats(row):
    return tuple(row[f] for f in STAT_FIELDS) if row else (0,) * len(STAT_FIELDS)


async def chat_stats(chat_id, period):
    return _stats(await pool.fetchrow("SELECT * FROM chat_stats WHERE chat_id = $1 AND period = $2", chat_id, period))


async def member_stats(chat_id, user_id, period):
    return _stats(await pool.fetchrow("SELECT * FROM member_stats WHERE chat_id = $1 AND user_id = $2 AND period = $3",
                                      chat_id, user_id, period))


async def top(chat_id, period, field="mes", limit=10):
    """Лучшие участники по счётчику: [(id, имя, значение)]"""
    assert field in STAT_FIELDS
    rows = await pool.fetch(
        f"SELECT s.user_id, m.name, s.{field} AS value FROM member_stats s "
        f"JOIN members m USING (chat_id, user_id) WHERE s.chat_id = $1 AND s.period = $2 AND s.{field} > 0 "
        f"ORDER BY s.{field} DESC, m.name LIMIT $3", chat_id, period, limit)
    return [(r["user_id"], r["name"], r["value"]) for r in rows]


# БОТ В ЧАТАХ
IN_CHAT = ("member", "administrator", "restricted", "creator")


async def set_bot_status(chat_id, status, rights, source, member_count=None, chat_type=None, title=None):
    """Записывает статус бота в чате; в историю — только если статус или права изменились"""
    rights_json = None if rights is None else json.dumps(rights, sort_keys=True)
    async with pool.acquire() as conn, conn.transaction():
        await conn.execute(
            "INSERT INTO chats (id, title) VALUES ($1, $2) "
            "ON CONFLICT (id) DO UPDATE SET title = COALESCE(EXCLUDED.title, chats.title)", chat_id, title)
        changed = await conn.fetchval(
            "SELECT bot_status IS DISTINCT FROM $2 OR bot_rights IS DISTINCT FROM $3::jsonb FROM chats WHERE id = $1",
            chat_id, status, rights_json)
        await conn.execute(
            "UPDATE chats SET bot_status = $2, bot_rights = $3::jsonb, checked_at = now(), "
            "bot_status_at = CASE WHEN $4 THEN now() ELSE bot_status_at END, "
            "member_count = COALESCE($5, member_count), chat_type = COALESCE($6, chat_type) WHERE id = $1",
            chat_id, status, rights_json, changed, member_count, chat_type)
        if changed:
            await conn.execute("INSERT INTO bot_status_history (chat_id, status, rights, source) "
                               "VALUES ($1, $2, $3::jsonb, $4)", chat_id, status, rights_json, source)
    return changed


async def chats_to_check():
    """Чаты для сверки: все, где бот считается состоящим, и те, где статус неизвестен"""
    rows = await pool.fetch("SELECT id FROM chats WHERE bot_status IS NULL OR bot_status = ANY($1::text[])",
                            list(IN_CHAT))
    return [r["id"] for r in rows]
