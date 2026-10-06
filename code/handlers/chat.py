"""Жизнь бота в чатах: добавили/исключили/поменяли права, служебные сообщения, вход и выход участников"""
import asyncio
import logging

from aiogram import Bot, F, Router
from aiogram.enums import ContentType
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError
from aiogram.types import ChatMemberUpdated, Message

import db

router = Router()

WELCOME = ('<b>Привет группа {title}!</b>\n\nВсе функции вы можете узнать по команде /help! Для того, чтобы '
           'уведомления по имени и команда /all нормально функционировали, необходимо чтобы каждый участник '
           'группы написал хотя бы одно сообщение в чат! Также для того, чтобы системные сообщения удалялись '
           'автоматически, необходимо боту выдать права администратора!')


def rights_of(member):
    """Права бота из ChatMember: все поля can_* (у админа — что он может, у ограниченного — что ему можно)"""
    data = member.model_dump()
    return {k: v for k, v in data.items() if k.startswith("can_") and isinstance(v, bool)} or None


# СТАТУС БОТА: событие Telegram при любом изменении (добавили, повысили, ограничили, исключили)
@router.my_chat_member()
async def bot_status_changed(update: ChatMemberUpdated, bot: Bot):
    if update.chat.type == "private":
        return
    member = update.new_chat_member
    count = None
    if member.status in db.IN_CHAT:
        try:
            count = await bot.get_chat_member_count(update.chat.id)
        except Exception:
            pass
    changed = await db.set_bot_status(update.chat.id, member.status, rights_of(member), "update",
                                      member_count=count, chat_type=update.chat.type, title=update.chat.title)
    if changed:
        logging.info("Бот в чате %s (%s): %s", update.chat.id, update.chat.title, member.status)

    # бота только что добавили — приветствие
    old = update.old_chat_member.status
    if member.status in ("member", "administrator") and old in ("left", "kicked"):
        try:
            await bot.send_message(update.chat.id, WELCOME.format(title=update.chat.title or ""))
        except Exception:
            pass


async def check_chat(bot: Bot, chat_id):
    """Сверка статуса бота с Telegram — ловит изменения, пока бот был выключен"""
    try:
        chat = await bot.get_chat(chat_id)
        member = await bot.get_chat_member(chat_id, bot.id)
        count = await bot.get_chat_member_count(chat_id) if member.status in db.IN_CHAT else None
        await db.set_bot_status(chat_id, member.status, rights_of(member), "check",
                                member_count=count, chat_type=chat.type, title=chat.title)
    except TelegramForbiddenError:
        # исключён или чат удалён: данные не трогаем, фиксируем, что бота там нет
        await db.set_bot_status(chat_id, "kicked", None, "check")
    except TelegramBadRequest as e:
        if "chat not found" in str(e).lower() or "upgraded to a supergroup" in str(e).lower():
            await db.set_bot_status(chat_id, "left", None, "check")
        else:
            logging.warning("Сверка чата %s: %s", chat_id, e)


async def check_all(bot: Bot):
    for chat_id in await db.chats_to_check():
        await check_chat(bot, chat_id)
        await asyncio.sleep(0.5)  # без спешки — лимиты Telegram API


# НОВЫЕ УЧАСТНИКИ: служебное сообщение удаляется (если включено и есть права)
@router.message(F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def new_members(message: Message):
    await db.ensure_chat(message.chat.id, message.chat.title)
    if any(u.id == message.bot.id for u in message.new_chat_members):
        return  # о самом боте — приветствие в bot_status_changed
    if await db.get_setting(message.chat.id, "delete_service"):
        try:
            await message.delete()
        except Exception:
            pass


# ГРУППА СТАЛА СУПЕРГРУППОЙ — новый id чата
@router.message(F.content_type.in_([ContentType.MIGRATE_TO_CHAT_ID, ContentType.MIGRATE_FROM_CHAT_ID]))
async def chat_migrated(message: Message):
    if message.migrate_to_chat_id:
        await db.migrate_chat(message.chat.id, message.migrate_to_chat_id)
    elif message.migrate_from_chat_id:
        await db.migrate_chat(message.migrate_from_chat_id, message.chat.id)


# УЧАСТНИК ВЫШЕЛ: статистика остаётся, участник больше не упоминается
@router.message(F.content_type == ContentType.LEFT_CHAT_MEMBER)
async def left_member(message: Message):
    if message.left_chat_member.id == message.bot.id:
        return
    await db.member_left(message.chat.id, message.left_chat_member.id)
    if await db.get_setting(message.chat.id, "delete_service"):
        try:
            await message.delete()
        except Exception:
            pass


# ТЕХНИЧЕСКИЕ СООБЩЕНИЯ
@router.message(F.content_type.in_([
    ContentType.NEW_CHAT_TITLE,
    ContentType.NEW_CHAT_PHOTO,
    ContentType.PINNED_MESSAGE,
    ContentType.VIDEO_CHAT_ENDED,
    ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED
]))
async def chat_events(message: Message):
    if message.new_chat_title:
        await db.ensure_chat(message.chat.id, message.new_chat_title)
    if await db.get_setting(message.chat.id, "delete_service"):
        try:
            await message.delete()
        except Exception:
            pass
