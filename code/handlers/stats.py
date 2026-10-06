"""Статистика чата и участников: за всё время, за месяц, топ и итоги месяца"""
import re
from datetime import date

from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

import db
from nlp import clean_name, genitive, h

from .common import count, in_group

router = Router()

MONTHS = ["январь", "февраль", "март", "апрель", "май", "июнь", "июль", "август", "сентябрь", "октябрь",
          "ноябрь", "декабрь"]


def stat_lines(total, month):
    return (f'<b>- За всё время</b> / <b>За месяц -</b>\n'
            f'<b>>></b> Сообщений в базе <b>[ {total[0]} / {month[0]} ]</b>\n\n'
            f'<b>></b> Ответов <b>- [ {total[1]} / {month[1]} ]</b>\n'
            f'<b>></b> Команд <b>- [ {total[2]} / {month[2]} ]</b>\n'
            f'<b>></b> Ссылок <b>- [ {total[3]} / {month[3]} ]</b>\n'
            f'<b>></b> Стикеров <b>- [ {total[5]} / {month[5]} ]</b>\n'
            f'<b>></b> Медиа файлов <b>- [ {total[4]} / {month[4]} ]</b>\n'
            f'<b>></b> Голос/Кружочки <b>- [ {total[6]} / {month[6]} ]</b>')


def month_title(period):
    year, month = period.split("-")
    return f"{MONTHS[int(month) - 1]} {year}"


def parse_period(arg):
    """«2026-09», «прошлый» или ничего (текущий месяц)"""
    today = date.today()
    if not arg:
        return db.month_key(today)
    arg = arg.strip().lower()
    if arg in ("прошлый", "prev", "last"):
        first = today.replace(day=1)
        return db.month_key(date(first.year - (first.month == 1), (first.month - 2) % 12 + 1, 1))
    if re.fullmatch(r"\d{4}-\d{2}", arg) and 1 <= int(arg[5:]) <= 12:
        return arg
    return None


@router.message(Command('stat_group'))
async def stat_group(message: Message):
    if not in_group(message):
        return
    await count(message, 3, 1)
    total = await db.chat_stats(message.chat.id, "all")
    month = await db.chat_stats(message.chat.id, db.month_key())
    await message.answer(f'<b>| СТАТИСТИКА ГРУППЫ |</b>\n\n'
                         f'<b>>></b> В целом сообщений <b>[ {message.message_id} ]</b>\n\n' + stat_lines(total, month))


@router.message(Command('stat_user'))
async def stat_user(message: Message):
    if not in_group(message):
        return
    await count(message, 3, 1)
    total = await db.member_stats(message.chat.id, message.from_user.id, "all")
    month = await db.member_stats(message.chat.id, message.from_user.id, db.month_key())
    name = genitive(clean_name(message.from_user.first_name).replace(" ", "")) or message.from_user.first_name
    await message.answer(f'<b>| СТАТИСТИКА {h(name.upper())} |</b>\n\n' + stat_lines(total, month))


@router.message(Command('top'))
async def top(message: Message, command: CommandObject):
    """Самые активные участники по сообщениям: за месяц или за всё время (/top all)"""
    if not in_group(message):
        return
    await count(message, 3, 1)
    all_time = (command.args or "").strip().lower() in ("all", "всё", "все")
    period = "all" if all_time else db.month_key()
    rows = await db.top(message.chat.id, period, "mes", 10)
    if not rows:
        await message.answer("Статистики пока нет!")
        return
    title = "за всё время" if all_time else f"за {month_title(period)}"
    # без ссылок-упоминаний: иначе каждый из топа получил бы уведомление
    lines = [f"<b>{i}.</b> {h(name.title())} — <b>{value}</b>" for i, (_, name, value) in enumerate(rows, 1)]
    await message.answer(f"<b>| ТОП УЧАСТНИКОВ {title.upper()} |</b>\n\n" + "\n".join(lines),
                         disable_notification=True)


CATEGORIES = [("mes", "Больше всех писали"), ("rep", "Больше всех отвечали"), ("sti", "Короли стикеров"),
              ("voi", "Больше всех голосовых и кружочков"), ("med", "Больше всех медиа")]


@router.message(Command('month'))
async def month_results(message: Message, command: CommandObject):
    """Итоги месяца — только по команде: топ-3 в каждой категории"""
    if not in_group(message):
        return
    await count(message, 3, 1)
    period = parse_period(command.args)
    if period is None:
        await message.reply("Укажите месяц в формате <b>2026-09</b> или <b>прошлый</b>")
        return

    blocks = []
    for field, title in CATEGORIES:
        rows = await db.top(message.chat.id, period, field, 3)
        if rows:
            blocks.append(f"<b>{title}:</b>\n" + "\n".join(
                f"{i}. {h(name.title())} — {value}" for i, (_, name, value) in enumerate(rows, 1)))
    if not blocks:
        await message.answer(f"За {month_title(period)} статистики нет!")
        return
    totals = await db.chat_stats(message.chat.id, period)
    await message.answer(f"<b>| ИТОГИ: {month_title(period).upper()} |</b>\n\n"
                         f"Сообщений в чате: <b>{totals[0]}</b>\n\n" + "\n\n".join(blocks))
