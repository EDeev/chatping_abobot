"""Настройки бота в чате: кнопки-переключатели, менять могут администраторы"""
from aiogram import Bot, F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

import db

from .common import count, in_group, is_admin

router = Router()

LABELS = {
    "mentions_enabled": "Упоминания по имени",
    "voice_names": "Имена в голосовых (через Google)",
    "events_enabled": "Текстовые ивенты",
    "delete_service": "Удаление служебных сообщений",
}


async def keyboard(chat_id):
    current = await db.settings(chat_id)
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"{'✅' if current[key] else '❌'} {label}", callback_data=f"set:{key}")]
        for key, label in LABELS.items()
    ])


@router.message(Command('settings'))
async def show_settings(message: Message):
    if not in_group(message):
        await message.reply('Настройки есть только у групп — вызовите команду в чате!')
        return
    await count(message, 3, 1)
    await message.answer('<b>| НАСТРОЙКИ ЧАТА |</b>\n\nНажмите, чтобы включить или выключить. Менять настройки '
                         'могут администраторы.', reply_markup=await keyboard(message.chat.id))


@router.callback_query(F.data.startswith("set:"))
async def toggle(call: CallbackQuery, bot: Bot):
    key = call.data[4:]
    if key not in LABELS:
        return
    if not await is_admin(bot, call.message.chat.id, call.from_user.id):
        await call.answer("Настройки могут менять только администраторы", show_alert=True)
        return
    value = await db.toggle_setting(call.message.chat.id, key)
    await call.message.edit_reply_markup(reply_markup=await keyboard(call.message.chat.id))
    await call.answer(f"{LABELS[key]}: {'включено' if value else 'выключено'}")


async def set_events(message: Message, enable):
    if not in_group(message):
        return
    await count(message, 3, 1)
    if await db.get_setting(message.chat.id, "events_enabled") == enable:
        await message.answer("У вас уже включены текстовые ивенты!" if enable
                             else "У вас уже отключены текстовые ивенты!")
        return
    await db.toggle_setting(message.chat.id, "events_enabled")
    await message.answer("Текстовые ивенты включены!" if enable else "Текстовые ивенты отключены!")


@router.message(Command('start_bot'))
async def opening(message: Message):
    await set_events(message, True)


@router.message(Command('stop_bot'))
async def closing(message: Message):
    await set_events(message, False)
