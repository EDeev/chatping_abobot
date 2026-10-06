from datetime import date

import pytest

import db
import nlp
from handlers import common, mentions, stats


def test_chunks_respect_limit():
    parts = [f'<a href="tg://user?id={i}">Участник{i}</a>' for i in range(500)]
    messages = mentions.chunks(parts, " вас вызывает Маша", limit=4096)
    assert len(messages) > 1 and all(len(m) <= 4096 for m in messages)
    assert messages[-1].endswith(" вас вызывает Маша")
    assert sum(m.count("tg://user") for m in messages) == 500


class Msg:
    def __init__(self, chat_id, user_id):
        from types import SimpleNamespace
        self.chat = SimpleNamespace(id=chat_id)
        self.from_user = SimpleNamespace(id=user_id)


async def test_mentions_and_big_chat_cooldown(pool, fake_bot):
    await db.count(-1, 1, [1], "маша")
    await db.count(-1, 2, [1], "петя")
    small, big = fake_bot(size=10), fake_bot(size=500)

    text = await mentions.mention_in_text(small, Msg(-1, 2), "позови Машу")
    assert text == '<a href="tg://user?id=1">Маша</a>, тебя упомянули)'
    assert await mentions.mention_in_text(small, Msg(-1, 1), "я Маша") is None  # себя не зовём

    mentions._last_mention.clear()
    common._size_cache.clear()  # размер чата кэшируется на 10 минут
    assert await mentions.mention_names(big, Msg(-1, 2), ["маша"])
    assert await mentions.mention_names(big, Msg(-1, 2), ["маша"]) is None  # в большом чате — раз в минуту
    common._size_cache.clear()
    assert await mentions.mention_names(small, Msg(-1, 2), ["маша"])  # в маленьком — всегда


async def test_mentions_can_be_disabled(pool, fake_bot):
    await db.count(-1, 1, [1], "маша")
    await db.toggle_setting(-1, "mentions_enabled")
    assert await mentions.mention_in_text(fake_bot(), Msg(-1, 2), "Маша") is None


def test_parse_period():
    assert stats.parse_period("2026-09") == "2026-09"
    assert stats.parse_period("2026-13") is None
    assert stats.parse_period(None) == db.month_key(date.today())


@pytest.mark.parametrize("text,expected", [("ghbdtn vbh", True), ("hello world", False), ("http://x.ru", True),
                                           ("/help", False), ("привет", False), ("123 !!", False)])
def test_wrong_layout(text, expected):
    assert nlp.wrong_layout(text) is expected


def test_nlp_helpers():
    assert nlp.translator(["ghbdtn"]) == "привет"
    assert nlp.revers("Привет, мир!", True) == "Тевирп, рим!"
    assert nlp.lang_form(["кот"]) == "когот"
    assert nlp.mention(5, "иван_<b>") == '<a href="tg://user?id=5">Иван_&lt;B&gt;</a>'
    assert nlp.find_names("позови Машу и Петю, Машу!", {"маша", "петя"}) == ["маша", "петя"]


def test_bot_imports():
    import bot  # noqa: F401
