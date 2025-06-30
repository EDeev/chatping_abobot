from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, FSInputFile
from aiogram.filters import Command, CommandStart
from aiogram.enums import ContentType

import logging, random, requests, os, re
import speech_recognition as sr
import soundfile as sf
from gtts import gTTS

from init import *
from script import *
import base

router = Router()

# НОВЫЕ УЧАСТНИКИ ГРУППЫ
@router.message(F.content_type == ContentType.NEW_CHAT_MEMBERS)
async def notification(message: Message):
    if not du.group_exists(message.chat.id):
        du.add_group(message.chat.id)

        group_id = du.get_group_id(message.chat.id)
        db.add_group(group_id)
        dg.created_group(group_id)

        await bot.send_message(
            message.chat.id, 
            f'*Привет группа {message.chat.title}!*\n\n'
            f'Все функции вы можете узнать по команде /help! Для того, чтобы '
            f'уведомления по имени и команда /all нормально функционировали, '
            f'необходимо чтобы каждый участник группы написал хотя бы одно '
            f'сообщение в чат! Также для того, чтобы системные сообщения удалялись '
            f'автоматически, необходимо боту выдать права администратора!'
        )
    else:
        try:
            await message.delete()
        except Exception:
            return

# ОБНОВЛЕНИЕ АЙДИ ГРУППЫ
@router.message(F.content_type.in_([ContentType.MIGRATE_TO_CHAT_ID, ContentType.MIGRATE_FROM_CHAT_ID]))
async def chat_reload(message: Message):
    if du.group_exists(message.migrate_from_chat_id):
        du.update_group_id(du.get_group_id(message.migrate_from_chat_id), message.migrate_to_chat_id)

# КОМАНДЫ HELP И START
@router.message(CommandStart())
@router.message(Command('help'))
async def helps(message: Message):
    if message.chat.id > 0:
        user_id = message.from_user.id
        if not du.user_exists(user_id):
            du.add_user(user_id)
    else:
        group_id, user_id = message.chat.id, message.from_user.id
        if not du.user_exists(user_id):
            du.add_user(user_id)
        if not du.group_exists(group_id):
            du.add_group(group_id)
        upd_stat(user_id, group_id, 3, message.from_user.first_name, True)

    buttons = [
        [InlineKeyboardButton(text="КОМАНДЫ", callback_data="com"),
         InlineKeyboardButton(text="ИВЕНТЫ", callback_data="even")],
        [InlineKeyboardButton(text="АВТОР", callback_data="auth"),
         InlineKeyboardButton(text="ФУНКЦИИ", callback_data="fun")]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    try:
        await bot.send_voice(
            chat_id=message.chat.id, 
            voice=FSInputFile('../data/tts.ogg'),
            caption='*-* Этот АБОБОТ поможет вам приятно провести время в чате с различными командами, '
                   'ивентами и удобными функциями, которые облегчают использование чата)\n\n'
                   '*-* Также прошу если вам понравился бот, оставить отзыв о его использовании на '
                   'команду /report)', 
            reply_markup=keyboard
        )
    except Exception:
        await bot.send_message(
            chat_id=message.chat.id,
            text='*-* Этот АБОБОТ поможет вам приятно провести время в чате с различными командами, '
                'ивентами и удобными функциями, которые облегчают использование чата)\n\n'
                '*-* Также прошу если вам понравился бот, оставить отзыв о его использовании на '
                'команду /report)', 
            reply_markup=keyboard
        )

# INLINE КЛАВИАТУРА ОБРАБОТЧИКИ
@router.callback_query(F.data == "auth")
async def author(call: CallbackQuery):
    await call.message.answer(
        text='*| АВТОР |*\n\n*>>* Этот бот, как бы это не печально звучало, но одна из лучших'
             ' моих работ и если кого-нибудь у меня получится действительно достойный продукт,'
             ' вы сможете о нём узнать в моём телеграм канале *@programium*'
    )

@router.callback_query(F.data == "fun")
async def function(call: CallbackQuery):
    await call.message.answer(
        text='*| ФУНКЦИИ |*\n\n*1.* Возможность перевода случайно написанного текста на '
             'транслите\n*2.* Ведение обширной статистики сообщений\n*3.* Упоминание участника '
             'при написании его имени в чате\n*4.* Автоматическое удаление системных сообщений'
    )

@router.callback_query(F.data == "com")
async def commands(call: CallbackQuery):
    await call.message.answer(
        text='*| КОМАНДЫ |*\n\n*/all* - упомянуть всех в чате\n*/help* - полный список функций\n'
             '*/recognize* - транскрипция отмеченного голосового сообщения в текст\n'
             '*/stat_group* - полная статистика группы\n*/stat_user* - полная статистика '
             'отправителя\n*/edit и /back_edit* - первая команда даёт возможность '
             'сменить имя для упоминаний на любое слово, а вторая для возврата динамического '
             'имени\n*/start_bot и /stop_bot* - возможность отключения текстовых ивентов'
    )

@router.callback_query(F.data == "even")
async def events(call: CallbackQuery):
    await call.message.answer(
        text='*| ИВЕНТЫ |*\n\n*"Чмокнуть"* - сделать кому-нибудь приятно\n*"Отмудохать"* - '
             'выместить злость на кого-нибудь\n*"Число от ... до ..."* - случайное значение из '
             'диапозона\n*"Подраться с ..."* - повод кого-нибудь побить\n*"Переведи (..) - ..."* '
             '- перевод слова на керпичный язык\n*"Дай блять совет!"* - даёт рандомный охуенный '
             'совет\n*"Переверни - ..."* - переворачивает слова в предложении\n*"Озвучь - ..."* '
             '- озвучивает написанный текст'
    )

# КОМАНДА ALL
@router.message(Command('all'))
async def every(message: Message):
    if message.chat.id < 0:
        upd_stat(message.from_user.id, message.chat.id, 3, message.from_user.first_name, True)
        try:
            await message.reply(
                notice(du.get_user_id(message.from_user.id), True, 
                      du.get_group_id(message.chat.id), message.from_user.id)
            )
        except Exception:
            await message.reply('В группе состоит менее 3х человек, из-за чего команда не работает!')
    else:
        await message.reply('Эта команда предназначена для вызова в чате!')

# КОМАНДА RECOGNIZE
@router.message(Command("recognize"))
async def recognise(message: Message):
    user_id = du.get_user_id(message.from_user.id)

    if message.reply_to_message and message.reply_to_message.voice:
        num = random.randint(1000, 9999)
        audio = f"../data/voices/{user_id}_{num}.oga"

        file_id = message.reply_to_message.voice.file_id
        file = await bot.get_file(file_id)
        file_path = file.file_path
        await bot.download_file(file_path, audio)
        
        data, samplerate = sf.read(audio)
        os.remove(audio)
        audio = f"../data/voices/{user_id}_{num}.wav"
        sf.write(audio, data, samplerate)

        af = sr.AudioFile(audio)
        r = sr.Recognizer()
        with af as source:
            r.pause_threshold = 100
            source = r.listen(source)

        try:
            mes = await bot.send_message(
                chat_id=message.chat.id, 
                text="Распознавание.....", 
                reply_to_message_id=message.reply_to_message.message_id
            )
            try:
                query = r.recognize_google(source, language='ru-RU')
                os.remove(audio)
                await mes.edit_text(f'*{message.reply_to_message.from_user.first_name} сказал(a)* "{query}"')
            except Exception:
                try: 
                    os.remove(audio)
                except Exception: 
                    pass
                await mes.edit_text("Распознать сообщение не удалось!")
        except Exception as e:
            print(repr(e))
            pass

# СТАТИСТИКА ГРУППЫ
@router.message(Command('stat_group'))
async def stat_group(message: Message):
    if message.chat.id < 0:
        upd_stat(message.from_user.id, message.chat.id, 3, message.from_user.first_name, True)
        group_id = du.get_group_id(message.chat.id)

        group = db.stat_group(group_id)
        month = db.month_stat_group(group_id)

        await message.answer(
            text=f'*| СТАТИСТИКА ГРУППЫ |*\n\n'
                 f'*>>* В целом сообщений *[ {message.message_id} ]*\n\n'
                 f'*- За всё время* / *За месяц -*\n'
                 f'*>>* Сообщений в базе *[ {group[0]} / {month[0]} ]*\n\n'
                 f'*>* Ответов *- [ {group[1]} / {month[1]} ]*\n'
                 f'*>* Команд *- [ {group[2]} / {month[2]} ]*\n'
                 f'*>* Ссылок *- [ {group[3]} / {month[3]} ]*\n'
                 f'*>* Стикеров *- [ {group[5]} / {month[5]} ]*\n'
                 f'*>* Медиа файлов *- [ {group[4]} / {month[4]} ]*\n'
                 f'*>* Голос/Кружочки *- [ {group[6]} / {month[6]} ]*'
        )

# СТАТИСТИКА ПОЛЬЗОВАТЕЛЯ
@router.message(Command('stat_user'))
async def stat_user(message: Message):
    if message.chat.id < 0:
        upd_stat(message.from_user.id, message.chat.id, 3, message.from_user.first_name, True)
        user_id, group_id = du.get_user_id(message.from_user.id), du.get_group_id(message.chat.id)

        group = dg.stat_user(user_id, group_id)
        month = dm.stat_user(user_id, group_id)

        namer = "".join(re.sub(r'[^\w\s]', '', message.from_user.first_name).split())
        name = morph.parse(namer)[0].inflect({"gent"})

        if name is None: 
            name = namer
        else: 
            name = name.word

        await message.answer(
            text=f'*| СТАТИСТИКА {name.upper()} |*\n\n'
                 f'*- За всё время* / *За месяц -*\n'
                 f'*>>* Сообщений в базе *[ {group[0]} / {month[0]} ]*\n\n'
                 f'*>* Ответов *- [ {group[1]} / {month[1]} ]*\n'
                 f'*>* Команд *- [ {group[2]} / {month[2]} ]*\n'
                 f'*>* Ссылок *- [ {group[3]} / {month[3]} ]*\n'
                 f'*>* Стикеров *- [ {group[5]} / {month[5]} ]*\n'
                 f'*>* Медиа файлов *- [ {group[4]} / {month[4]} ]*\n'
                 f'*>* Голос/Кружочки *- [ {group[6]} / {month[6]} ]*'
        )

# РЕДАКТИРОВАНИЕ ИМЕНИ
@router.message(Command('edit'))
async def update(message: Message):
    if message.chat.id < 0:
        upd_stat(message.from_user.id, message.chat.id, 3, message.from_user.first_name, True)
        user_id, group_id = du.get_user_id(message.from_user.id), du.get_group_id(message.chat.id)

        text_edit = re.sub(r'[^\w\s]', '', message.text.lower()).split()
        if len(text_edit) == 2:
            name = morph.parse(text_edit[1])[0]

            if name is None: 
                name = text_edit[1]
            else: 
                name = name.normal_form

            if name not in list(map(lambda x: x[0], dg.all_names(group_id))):
                if not db.edit_user_exists(user_id):
                    db.add_edit_user(user_id)

                dg.update_name(user_id, group_id, name)
                await message.reply(f'{name.title()}, ваше имя было успешно изменено)')
            else:
                await message.reply(f'{message.from_user.first_name.lower().title()}, такое имя уже присутствует в чате!')
        else:
            await message.reply('Вы не правильно ввели имя! Имя должно быть '
                               'из одного слова и идти сразу после команды!')

# ВОЗВРАТ К ДИНАМИЧЕСКОМУ ИМЕНИ
@router.message(Command('back_edit'))
async def update_return(message: Message):
    if message.chat.id < 0:
        upd_stat(message.from_user.id, message.chat.id, 3, message.from_user.first_name, True)
        user_id, group_id = du.get_user_id(message.from_user.id), du.get_group_id(message.chat.id)
        name = re.sub(r'[^\w\s]', '', message.from_user.first_name.lower())

        if db.edit_user_exists(user_id):
            db.del_edit_user(user_id)
            dg.update_name(user_id, group_id, name)

            await message.reply(f'{name.title()}, вы успешно вернулись к динамическому изменению имени)')
        else:
            await message.reply(f'{name.title()}, вы не устанавливали постоянное имя!')

# ВКЛЮЧЕНИЕ ТЕКСТОВЫХ ИВЕНТОВ
@router.message(Command('start_bot'))
async def opening(message: Message):
    if message.chat.id < 0:
        upd_stat(message.from_user.id, message.chat.id, 3, message.from_user.first_name, True)

        group_id = du.get_group_id(message.chat.id)
        if db.check_status(group_id):
            await message.answer("У вас уже включены текстовые ивенты!")
        else:
            db.update_status(group_id)
            await message.answer("Текстовые ивенты включены!")

# ОТКЛЮЧЕНИЕ ТЕКСТОВЫХ ИВЕНТОВ
@router.message(Command('stop_bot'))
async def closing(message: Message):
    if message.chat.id < 0:
        upd_stat(message.from_user.id, message.chat.id, 3, message.from_user.first_name, True)

        group_id = du.get_group_id(message.chat.id)
        if db.check_status(group_id):
            db.update_status(group_id)
            await message.answer("Текстовые ивенты отключены!")
        else:
            await message.answer("У вас уже отключены текстовые ивенты!")

# УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЕЙ АВТОМАТИЧЕСКИ
@router.message(F.content_type == ContentType.LEFT_CHAT_MEMBER)
async def delete(message: Message):
    if du.user_exists(message.left_chat_member.id):
        user_id, group_id = du.get_user_id(message.left_chat_member.id), du.get_group_id(message.chat.id)

        dg.del_user(group_id, user_id)
        if db.group_exists_month(group_id):
            if dm.user_exists(user_id, group_id): 
                dm.del_user(group_id, user_id)

        try: 
            await message.delete()
        except Exception: 
            return

# УДАЛЕНИЕ ТЕХНИЧЕСКИХ СООБЩЕНИЙ
@router.message(F.content_type.in_([
    ContentType.NEW_CHAT_TITLE, 
    ContentType.NEW_CHAT_PHOTO, 
    ContentType.PINNED_MESSAGE,
    ContentType.VIDEO_CHAT_ENDED,
    ContentType.VIDEO_CHAT_PARTICIPANTS_INVITED
]))
async def chat_events(message: Message):
    try: 
        await message.delete()
    except Exception: 
        return

# МЕДИА ФАЙЛЫ
@router.message(F.content_type.in_([
    ContentType.LOCATION, 
    ContentType.CONTACT, 
    ContentType.VIDEO, 
    ContentType.PHOTO, 
    ContentType.AUDIO, 
    ContentType.DOCUMENT
]))
async def media(message: Message):
    if message.chat.id < 0: 
        upd_stat(message.from_user.id, message.chat.id, 5, message.from_user.first_name, True)

# ГОЛОСОВЫЕ СООБЩЕНИЯ И КРУЖОЧКИ
@router.message(F.content_type.in_([ContentType.VOICE, ContentType.VIDEO_NOTE]))
async def voice(message: Message):
    if message.chat.id < 0: 
        upd_stat(message.from_user.id, message.chat.id, 7, message.from_user.first_name, True)

    if message.voice and message.chat.id < 0:
        if message.voice.duration <= 60:
            user_id = du.get_user_id(message.from_user.id)
            
            num = random.randint(1000, 9999)
            audio = f"../data/voices/{user_id}_{num}.oga"

            file_id = message.voice.file_id
            file = await bot.get_file(file_id)
            file_path = file.file_path
            await bot.download_file(file_path, audio)

            data, samplerate = sf.read(audio)
            os.remove(audio)
            audio = f"../data/voices/{user_id}_{num}.wav"
            sf.write(audio, data, samplerate)

            af = sr.AudioFile(audio)
            r = sr.Recognizer()
            with af as source:
                r.pause_threshold = 100
                source = r.listen(source)

            try:
                query = r.recognize_google(source, language='ru-RU')
                os.remove(audio)

                group_id = message.chat.id
                unsigned = re.sub(r'[^\w\s]', '', query.lower()).split()
                first_form = [morph.parse(i)[0].normal_form for i in unsigned]
                names = [_ for _ in first_form if _ in list(map(lambda x: x[0], dg.all_names(du.get_group_id(group_id))))]
                
                if names:
                    await message.reply(notice(names, False, du.get_group_id(group_id), message.from_user.id))
                    return
                
            except Exception:
                try: 
                    os.remove(audio)
                except Exception: 
                    pass

# СТИКЕРЫ
@router.message(F.content_type == ContentType.STICKER)
async def stick(message: Message):
    if message.chat.id < 0: 
        upd_stat(message.from_user.id, message.chat.id, 6, message.from_user.first_name, True)

# ТЕКСТОВЫЕ ИВЕНТЫ
@router.message(F.content_type == ContentType.TEXT)
async def send_events(message: Message):
    group_id, user_id, name = message.chat.id, message.from_user.id, message.from_user.first_name

    # ОБНОВЛЕНИЕ СТАТИСТИКИ
    if message.chat.id < 0:
        upd_stat(user_id, group_id, 1, name)  # СООБЩЕНИЙ
        if len(message.text) > 1 and message.text[0] == '/': 
            upd_stat(user_id, group_id, 3, name)  # КОМАНД
        if message.reply_to_message: 
            upd_stat(user_id, group_id, 2, name)  # ОТВЕТОВ НА СООБЩЕНИЯ

    # ПЕРЕМЕННЫЕ
    low_mes = message.text.lower()
    words = message.text.split()
    unsigned = re.sub(r'[^\w\s]', '', low_mes).split()
    first_form = [morph.parse(i)[0].normal_form for i in unsigned]
    
    if message.chat.id < 0:
        names = [_ for _ in first_form if _ in list(map(lambda x: x[0], dg.all_names(du.get_group_id(group_id))))]

    if len(words) >= 2:
        # ПОЛЕЗНЫЕ ФУНКЦИИ
        if len(words) == 5 and "число от" in low_mes:
            try:
                num1, num2 = int(low_mes.split()[2]), int(low_mes.split()[4])
                await message.answer(
                    text=f"Число *[ {random.randint(num1, num2)} ]*"
                )
            except ValueError:
                pass
            return

        if unsigned[0] == 'переведи':
            if "переведи - " in low_mes:
                await message.answer(lang_form([words[_] for _ in range(len(words)) if _ > 1]))
            elif f"переведи ({unsigned[1]}) - " in low_mes:
                if len(unsigned[1]) == 1:
                    await message.answer(lang_form([words[_] for _ in range(len(words)) if _ > 2], unsigned[1]))
            return

        if unsigned[0] == 'переверни':
            if "переверни - " in low_mes:
                await message.answer(revers(message.text[12:], True))
            elif "переверни полностью - " in low_mes:
                await message.answer(revers(message.text[22:], False))
            return

        if unsigned[0] == 'озвучь' and "озвучь - " in low_mes:
            text_to_voice = message.text[9:]
            tts = gTTS(text_to_voice, lang='ru')
            tts.save('../data/voices/voice.ogg')
            await bot.send_voice(
                chat_id=group_id, 
                voice=FSInputFile('../data/voices/voice.ogg'),
                caption=f"*{text_to_voice}*"
            )
            os.remove('../data/voices/voice.ogg')
            return

        # РАНДОМ ИВЕНТЫ
        if "подраться" == words[0].lower() and "с" == words[1].lower():
            text = " ".join([words[i] for i in range(len(words)) if i > 1])

            if random.randint(0, 1) == 0:
                await message.answer_photo(
                    photo=FSInputFile(f"../data/fight/({random.randint(1, 8)}).jpg"),
                    caption=f"{message.from_user.first_name}, ты был унижен {text.title()}"
                           f", с помощью {base.VAR_LOSE[random.randint(0, 3)]}"
                )
            else:
                await message.answer_photo(
                    photo=FSInputFile(f"../data/fight/({random.randint(1, 8)}).jpg"),
                    caption=f"{message.from_user.first_name}, ты победил в драке "
                           f"с {text.title()}, {base.VAR_WIN[random.randint(0, 1)]}"
                )

        # ИВЕНТ ВЗАИМОДЕЙСТВИЯ
        for word in base.TMOK_LIST:
            if word in low_mes:
                lst = [words[i] for i in range(len(words)) if i != 0]
                text = " ".join(lst)

                slv = morph.parse(words[0].lower())[0]
                await message.answer_photo(
                    photo=FSInputFile(f"../data/tmok/({random.randint(1, 4)}).jpg"),
                    caption=f"{message.from_user.first_name} "
                           f"{slv.inflect({'past', 'sing', 'indc'}).word} {text}"
                )

        for word in base.KILL_LIST:
            if word in low_mes:
                lst = [words[i] for i in range(len(words)) if i != 0]
                text = " ".join(lst)

                slv = morph.parse(words[0].lower())[0]
                await message.answer_photo(
                    photo=FSInputFile(f"../data/kill/({random.randint(1, 6)}).jpg"),
                    caption=f"{message.from_user.first_name} "
                           f"{slv.inflect({'past', 'sing', 'indc'}).word} {text}"
                )

        if (unsigned[0] in base.QUAT_LIST[0] and 
            unsigned[1] in base.QUAT_LIST[1] and 
            unsigned[2] in base.QUAT_LIST[2]):
            try:
                word = requests.get('http://fucking-great-advice.ru/api/random').json()
                await message.reply(word["text"])
            except:
                pass
            return

    if message.chat.id < 0:
        # УПОМИНАНИЯ ПО ИМЕНАМ
        if names:
            try:
                await message.reply(notice(names, False, du.get_group_id(group_id), user_id))
            except Exception:
                pass
            return

        # ПЕРЕВОДЧИК СЛОВ
        if (checker([i for i in low_mes], words, group_id, user_id, name.lower()) == len(low_mes) and 
            not any([engl_dict.check(i) for i in unsigned if len(i) > 1])):
            await message.reply(
                f"[{message.from_user.first_name}](tg://user_id?id={user_id}) *>* {translator(words)}"
            )
            return