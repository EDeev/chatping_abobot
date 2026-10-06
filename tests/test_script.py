import script
from init import du, dg


def test_md_and_plain():
    assert script.md("ivan_petrov *x*") == "ivan\\_petrov \\*x\\*"
    assert script.plain("[a]_b*") == "ab"


def test_join_names():
    assert script.join_names(["а"]) == "а"
    assert script.join_names(["а", "б"]) == "а и б"
    assert script.join_names(["а", "б", "в"]) == "а, б и в"


def test_translator_fixes_wrong_layout():
    assert script.translator(["ghbdtn", "vbh"]) == "привет мир"


def test_revers_and_lang_form():
    assert script.revers("Привет, мир!", True) == "Тевирп, рим!"
    assert script.lang_form(["кот"]) == "когот"


def test_stats_counters_and_mentions():
    chat, author, other, third = -100500, 1, 2, 3
    script.upd_stat(author, chat, 1, "Автор")
    script.upd_stat(other, chat, 1, "Иван_")
    script.upd_stat(other, chat, 1, "Иван_")
    script.upd_stat(third, chat, 2, "Пётр")

    group_id = du.get_group_id(chat)
    ivan = du.get_user_id(other)
    assert dg.stat_user(ivan, group_id)[0] == 2  # два сообщения — счётчик атомарный

    # упоминание: спецсимволы Markdown из имени внутри ссылки убираются, автор себя не упоминает
    text = script.notice(["иван_", "автор"], False, group_id, author)
    assert text == "[Иван](tg://user?id=2), тебя упомянули)"
    assert script.notice(["автор"], False, group_id, author).startswith("[Автор]")

    every = script.notice(du.get_user_id(author), True, group_id, author)
    assert "[Иван](tg://user?id=2) и [Пётр](tg://user?id=3) вас вызывает Автор" == every


def test_bot_imports():
    import bot  # noqa: F401 — обработчики и роутер собираются без ошибок


def test_month_reset():
    from datetime import date

    import bot
    from init import db, dm

    chat, user = -200300, 10
    script.upd_stat(user, chat, 1, "Маша")
    group_id = du.get_group_id(chat)
    member = du.get_user_id(user)

    assert bot.reset_month_if_needed(date(2026, 10, 6)) is False  # первый запуск — только запомнить
    assert dm.stat_user(member, group_id)[0] == 1
    assert bot.reset_month_if_needed(date(2026, 10, 20)) is False  # тот же месяц
    assert bot.reset_month_if_needed(date(2026, 11, 1)) is True
    assert dm.stat_user(member, group_id)[0] == 0 and db.month_stat_group(group_id)[0] == 0
    assert dg.stat_user(member, group_id)[0] == 1  # статистика за всё время не трогается
