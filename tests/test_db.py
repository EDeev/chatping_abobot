from datetime import date

import db


async def test_counters_all_time_and_month(pool):
    await db.count(-1, 10, [1, 3], "маша", "Чат", day=date(2026, 10, 6))
    await db.count(-1, 10, [1], "маша", day=date(2026, 10, 7))
    await db.count(-1, 10, [1], "маша", day=date(2026, 11, 1))
    assert (await db.member_stats(-1, 10, "all"))[:3] == (3, 0, 1)
    assert (await db.member_stats(-1, 10, "2026-10"))[0] == 2
    assert (await db.member_stats(-1, 10, "2026-11"))[0] == 1  # месяцы хранятся, а не обнуляются
    assert (await db.chat_stats(-1, "all"))[0] == 3


async def test_custom_name_survives_and_left_member(pool):
    await db.count(-1, 10, [1], "мария")
    await db.set_custom_name(-1, 10, "маша")
    await db.count(-1, 10, [1], "мария")
    assert await db.chat_names(-1) == {"маша": 10}
    await db.member_left(-1, 10)
    assert await db.chat_names(-1) == {}
    assert (await db.member_stats(-1, 10, "all"))[0] == 2  # статистика ушедшего остаётся


async def test_chat_migration_keeps_stats(pool):
    await db.count(-1, 10, [1], "маша")
    await db.migrate_chat(-1, -1001)
    assert (await db.member_stats(-1001, 10, "all"))[0] == 1
    assert not await db.chat_exists(-1)


async def test_bot_status_history(pool):
    assert await db.set_bot_status(-5, "member", {"can_send_messages": True}, "update", member_count=40)
    assert not await db.set_bot_status(-5, "member", {"can_send_messages": True}, "check")  # без изменений
    assert await db.set_bot_status(-5, "administrator", {"can_delete_messages": True}, "update")
    assert await db.set_bot_status(-5, "kicked", None, "check")
    history = await db.pool.fetch("SELECT status, source FROM bot_status_history WHERE chat_id = -5 ORDER BY id")
    assert [(r["status"], r["source"]) for r in history] == [
        ("member", "update"), ("administrator", "update"), ("kicked", "check")]
    assert await db.chats_to_check() == []  # из исключённого чата не проверяем
    assert await db.pool.fetchval("SELECT count(*) FROM active_chats") == 0


async def test_top(pool):
    for uid, name, n in ((1, "а", 3), (2, "б", 5), (3, "в", 1)):
        for _ in range(n):
            await db.count(-1, uid, [1], name)
    assert [(n, v) for _, n, v in await db.top(-1, "all", "mes", 2)] == [("б", 5), ("а", 3)]
