"""Упоминания: /all, упоминание по имени, своё имя для упоминаний"""
import time
from datetime import datetime, timezone

from aiogram import Bot, Router
from aiogram.filters import Command
from aiogram.types import Message

import config
import db
from nlp import clean_name, find_names, h, join_names, mention, morph

from .common import count, in_group, is_admin, is_big

router = Router()
TEXT_LIMIT = 4096
_last_mention = {}  # (чат, участник) → время последнего упоминания по имени


def chunks(parts, suffix, limit=TEXT_LIMIT):
    """Список упоминаний, разбитый на сообщения не длиннее лимита Telegram"""
    messages, current = [], []
    for part in parts:
        candidate = join_names(current + [part]) + suffix
        if current and len(candidate) > limit:
            messages.append(join_names(current))
            current = []
        current.append(part)
    messages.append(join_names(current) + suffix)
    return messages


async def mention_names(bot: Bot, message: Message, found):
    """Текст упоминания найденных в сообщении имён; в большом чате одного человека — не чаще раза в минуту"""
    chat_id, author = message.chat.id, message.from_user.id
    names = await db.chat_names(chat_id)
    targets = [(names[n], n) for n in found if n in names and names[n] != author]
    if not targets:
        return None

    if await is_big(bot, chat_id):
        now = time.monotonic()
        targets = [(uid, n) for uid, n in targets
                   if now - _last_mention.get((chat_id, uid), 0) >= config.MENTION_COOLDOWN]
        for uid, _ in targets:
            _last_mention[(chat_id, uid)] = now
        if not targets:
            return None

    links = [mention(uid, n) for uid, n in targets]
    return f"{links[0]}, тебя упомянули)" if len(links) == 1 else f"{join_names(links)} вас упомянули)"


async def mention_in_text(bot: Bot, message: Message, text):
    if not await db.get_setting(message.chat.id, "mentions_enabled"):
        return None
    found = find_names(text, set((await db.chat_names(message.chat.id)).keys()))
    return await mention_names(bot, message, found) if found else None


@router.message(Command('all'))
async def every(message: Message, bot: Bot):
    if not in_group(message):
        await message.reply('Эта команда предназначена для вызова в чате!')
        return
    await count(message, 3, 1)
    chat_id = message.chat.id
    big = await is_big(bot, chat_id)

    if big:
        # в большом чате — только админы, не чаще раза в 5 минут и только недавно писавшие
        if not await is_admin(bot, chat_id, message.from_user.id):
            await message.reply(f'В чатах больше {config.BIG_CHAT} участников /all доступна только администраторам!')
            return
        last = await db.last_all(chat_id)
        if last and (datetime.now(timezone.utc) - last).total_seconds() < config.ALL_COOLDOWN:
            await message.reply(f'В больших чатах /all можно вызывать раз в {config.ALL_COOLDOWN // 60} минут!')
            return
        members = await db.active_members(chat_id, config.ALL_ACTIVE_DAYS)
    else:
        members = await db.active_members(chat_id)

    others = [(uid, name) for uid, name in members if uid != message.from_user.id]
    if len(others) < 2:
        await message.reply('В группе состоит менее 3х человек, из-за чего команда не работает!')
        return

    author = await db.member_name(chat_id, message.from_user.id) or clean_name(message.from_user.first_name)
    parts = chunks([mention(uid, name) for uid, name in others], f" вас вызывает {h(author.title())}")
    await message.reply(parts[0])
    for part in parts[1:]:
        await message.answer(part)
    await db.mark_all(chat_id)


@router.message(Command('edit'))
async def edit_name(message: Message):
    if not in_group(message):
        return
    await count(message, 3, 1)
    words = clean_name(message.text).split()
    if len(words) != 2:
        await message.reply('Вы не правильно ввели имя! Имя должно быть из одного слова и идти сразу после команды!')
        return

    name = morph.parse(words[1])[0].normal_form or words[1]
    if name in await db.chat_names(message.chat.id):
        await message.reply(f'{h(message.from_user.first_name.title())}, такое имя уже присутствует в чате!')
        return
    await db.set_custom_name(message.chat.id, message.from_user.id, name)
    await message.reply(f'{h(name.title())}, ваше имя было успешно изменено)')


@router.message(Command('back_edit'))
async def back_edit(message: Message):
    if not in_group(message):
        return
    await count(message, 3, 1)
    name = clean_name(message.from_user.first_name)
    if await db.reset_custom_name(message.chat.id, message.from_user.id, name):
        await message.reply(f'{h(name.title())}, вы успешно вернулись к динамическому изменению имени)')
    else:
        await message.reply(f'{h(name.title())}, вы не устанавливали постоянное имя!')
