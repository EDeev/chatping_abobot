"""Текстовые сообщения: учёт статистики, ивенты, упоминания по имени, исправление раскладки; медиа и стикеры"""
import asyncio
import logging
import os
import random
import re
import tempfile

import requests
from aiogram import Bot, F, Router
from aiogram.enums import ContentType
from aiogram.types import FSInputFile, Message

import base
import db
from nlp import h, has_url, inflect_past, lang_form, mention, revers, translator, wrong_layout

from .common import count, in_group
from .mentions import mention_in_text

router = Router()


@router.message(F.content_type.in_([
    ContentType.LOCATION,
    ContentType.CONTACT,
    ContentType.VIDEO,
    ContentType.PHOTO,
    ContentType.AUDIO,
    ContentType.DOCUMENT
]))
async def media(message: Message):
    await count(message, 5, 1)


@router.message(F.content_type == ContentType.STICKER)
async def stick(message: Message):
    await count(message, 6, 1)


async def run_events(message: Message, bot: Bot, low_mes, words, unsigned):
    """Текстовые ивенты; True — если сообщение обработано ивентом"""
    if len(words) == 5 and "число от" in low_mes:
        try:
            num1, num2 = int(words[2]), int(words[4])
            await message.answer(f"Число <b>[ {random.randint(min(num1, num2), max(num1, num2))} ]</b>")
        except ValueError:
            pass
        return True

    if unsigned[0] == 'переведи':
        if "переведи - " in low_mes:
            await message.answer(h(lang_form(words[2:])))
        elif len(unsigned) > 1 and f"переведи ({unsigned[1]}) - " in low_mes and len(unsigned[1]) == 1:
            await message.answer(h(lang_form(words[3:], unsigned[1])))
        return True

    if unsigned[0] == 'переверни':
        if "переверни - " in low_mes:
            await message.answer(h(revers(message.text[12:], True)))
        elif "переверни полностью - " in low_mes:
            await message.answer(h(revers(message.text[22:], False)))
        return True

    if unsigned[0] == 'озвучь' and "озвучь - " in low_mes:
        from gtts import gTTS
        text_to_voice = message.text[9:]
        # синтез — в отдельном потоке и во временный файл
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "voice.mp3")
            try:
                await asyncio.to_thread(gTTS(text_to_voice, lang='ru').save, path)
            except Exception:
                logging.exception("gTTS")
                await message.reply("Озвучить не получилось, попробуйте позже")
                return True
            await message.answer_voice(voice=FSInputFile(path), caption=f"<b>{h(text_to_voice)}</b>")
        return True

    if words[0].lower() == "подраться" and words[1].lower() == "с":
        text = h(" ".join(words[2:]).title())
        name = h(message.from_user.first_name)
        if random.randint(0, 1) == 0:
            caption = f"{name}, ты был унижен {text}, с помощью {random.choice(base.VAR_LOSE)}"
        else:
            caption = f"{name}, ты победил в драке с {text}, {random.choice(base.VAR_WIN)}"
        await message.answer_photo(photo=FSInputFile(f"../data/fight/({random.randint(1, 8)}).jpg"), caption=caption)

    for folder, verbs, pictures in (("tmok", base.TMOK_LIST, 4), ("kill", base.KILL_LIST, 6)):
        if any(word in low_mes for word in verbs):
            await message.answer_photo(
                photo=FSInputFile(f"../data/{folder}/({random.randint(1, pictures)}).jpg"),
                caption=f"{h(message.from_user.first_name)} {h(inflect_past(words[0]))} {h(' '.join(words[1:]))}")

    if (len(unsigned) >= 3 and unsigned[0] in base.QUAT_LIST[0] and unsigned[1] in base.QUAT_LIST[1]
            and unsigned[2] in base.QUAT_LIST[2]):
        try:
            resp = await asyncio.to_thread(requests.get, 'http://fucking-great-advice.ru/api/random', timeout=5)
            await message.reply(h(resp.json()["text"]))
        except Exception:
            logging.warning("Сервис советов недоступен")
        return True
    return False


@router.message(F.content_type == ContentType.TEXT)
async def text_message(message: Message, bot: Bot):
    text = message.text
    low_mes = text.lower()
    words = text.split()
    unsigned = re.sub(r'[^\w\s]', '', low_mes).split()

    # статистика: сообщение, команда, ответ, ссылка — одним запросом
    if in_group(message):
        events = [1]
        if len(text) > 1 and text[0] == '/':
            events.append(3)
        if message.reply_to_message:
            events.append(2)
        if has_url(text):
            events.append(4)
        await count(message, *events)

    # ивенты (в группах выключаются /stop_bot; раньше флаг нигде не проверялся)
    if len(words) >= 2 and unsigned and (not in_group(message) or await db.get_setting(message.chat.id,
                                                                                         "events_enabled")):
        if await run_events(message, bot, low_mes, words, unsigned):
            return

    if not in_group(message):
        return

    reply = await mention_in_text(bot, message, text)
    if reply:
        await message.reply(reply)
        return

    if not has_url(text) and wrong_layout(text):
        await message.reply(f"{mention(message.from_user.id, message.from_user.first_name)} <b>></b> "
                            f"{h(translator(words))}")
