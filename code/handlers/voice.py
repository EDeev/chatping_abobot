"""Голосовые: /recognize и поиск имён в голосовых (Google Web Speech, выключается в /settings)"""
import asyncio
import logging
import os
import tempfile

import soundfile as sf
import speech_recognition as sr
from aiogram import Bot, F, Router
from aiogram.enums import ContentType
from aiogram.filters import Command
from aiogram.types import Message

import db
from nlp import find_names, h

from .common import count, in_group
from .mentions import mention_names

router = Router()


def recognize_file(oga_path):
    """Голосовое (OGG/Opus) → текст. Синхронно — вызывается в отдельном потоке"""
    data, samplerate = sf.read(oga_path)
    wav_path = oga_path[:-4] + ".wav"
    sf.write(wav_path, data, samplerate)

    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        r.pause_threshold = 100
        audio = r.listen(source)
    return r.recognize_google(audio, language='ru-RU')


async def recognize_voice(bot: Bot, file_id):
    """Распознавание без блокировки бота, файлы — во временной папке на запрос"""
    with tempfile.TemporaryDirectory() as tmp:
        oga = os.path.join(tmp, "voice.oga")
        file = await bot.get_file(file_id)
        await bot.download_file(file.file_path, oga)
        try:
            return await asyncio.to_thread(recognize_file, oga)
        except sr.UnknownValueError:  # речь не разобрана
            return None
        except Exception:
            logging.exception("Ошибка распознавания голосового")
            return None


@router.message(Command("recognize"))
async def recognise(message: Message, bot: Bot):
    if in_group(message):
        await count(message, 3, 1)
    voice = message.reply_to_message.voice if message.reply_to_message else None
    if not voice:
        await message.reply("Ответьте этой командой на голосовое сообщение!")
        return

    mes = await message.reply_to_message.reply("Распознавание.....")
    query = await recognize_voice(bot, voice.file_id)
    if query:
        await mes.edit_text(f'<b>{h(message.reply_to_message.from_user.first_name)} сказал(a)</b> "{h(query)}"')
    else:
        await mes.edit_text("Распознать сообщение не удалось!")


@router.message(F.content_type.in_([ContentType.VOICE, ContentType.VIDEO_NOTE]))
async def voice_message(message: Message, bot: Bot):
    if not in_group(message):
        return
    await count(message, 7, 1)

    # имена в голосовом: голос уходит в Google, поэтому в каждом чате можно выключить
    if not (message.voice and message.voice.duration <= 60):
        return
    settings = await db.settings(message.chat.id)
    if not (settings["voice_names"] and settings["mentions_enabled"]):
        return
    query = await recognize_voice(bot, message.voice.file_id)
    if not query:
        return
    found = find_names(query, set((await db.chat_names(message.chat.id)).keys()))
    text = await mention_names(bot, message, found) if found else None
    if text:
        await message.reply(text)
