"""Общее для обработчиков: учёт статистики, права, размер чата"""
import time

from aiogram import Bot
from aiogram.types import Message

import config
import db
from nlp import clean_name

_size_cache = {}


def in_group(message: Message):
    return message.chat.id < 0


async def count(message: Message, *var_ids):
    """Учёт события в группе от автора сообщения"""
    if in_group(message) and message.from_user and not message.from_user.is_bot:
        await db.count(message.chat.id, message.from_user.id, var_ids, clean_name(message.from_user.first_name),
                       message.chat.title)


async def is_admin(bot: Bot, chat_id, user_id):
    member = await bot.get_chat_member(chat_id, user_id)
    return member.status in ("creator", "administrator")


async def chat_size(bot: Bot, chat_id):
    """Число участников чата по Telegram (кэш на 10 минут)"""
    cached = _size_cache.get(chat_id)
    if cached and time.monotonic() - cached[1] < 600:
        return cached[0]
    try:
        size = await bot.get_chat_member_count(chat_id)
    except Exception:
        size = await db.member_count(chat_id)
    _size_cache[chat_id] = (size, time.monotonic())
    return size


async def is_big(bot: Bot, chat_id):
    return await chat_size(bot, chat_id) > config.BIG_CHAT
