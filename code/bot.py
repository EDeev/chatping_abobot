import logging, random, pymorphy2, requests
import asyncio, base, re, os, enchant, sql

from gtts import gTTS
from script import checker, translator, notice, lang_form, revers, upd_stat
from aiogram import Bot, Dispatcher, executor, types
from datetime import datetime as dt
# from filters import Admin

# log level
logging.basicConfig(level=logging.INFO)

# bot init
bot = Bot(token=base.TOKEN)
dp = Dispatcher(bot)
morph = pymorphy2.MorphAnalyzer()
engl_dict = enchant.Dict("en_US")

# инициализируем соединение с БД
db = sql.Base('../db/base.db')
du = sql.User('../db/users.db')
dg = sql.Group('../db/groups.db')
dm = sql.Month('../db/month.db')

# инициализируем фильтры
# dp.filters_factory.bind(Admin)


@dp.message_handler(content_types=["new_chat_members"])
async def notification(message: types.Message):
    if not du.group_exists(message.chat.id):
        du.add_group(message.chat.id)

        group_id = du.get_group_id(message.chat.id)
        db.add_group(group_id)
        dg.created_group(group_id)

        await bot.send_message(message.chat.id, f'<b>Привет группа {message.chat.title}!</b>\n\nВсе функции вы можете '
                                                f'узнать по команде /help! Для того, чтобы '
                                                f'уведомления по имени и команда /all нормально функционировали, '
                                                f'необходимо чтобы каждый участник группы написал хотя бы одно '
                                                f'сообщение в чат! Также для того, чтобы системные сообщения удалялись '
                                                f'автоматически, необходимо боту выдать права администратора!',
                               types.ParseMode.HTML)
    else:
        try:
            await message.delete()
        except Exception:
            return


# ОБНОВЛЕНИЕ АЙДИ ГРУППЫ
@dp.message_handler(content_types=['migrate_to_chat_id', 'migrate_from_chat_id'])
async def chat_reload(message: types.Message):
    if du.group_exists(message.migrate_from_chat_id):
        du.update_group_id(du.get_group_id(message.migrate_from_chat_id), message.migrate_to_chat_id)


# КОМАНДЫ
@dp.message_handler(commands=['start', 'help'])
async def helps(message: types.Message):
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

    buttons = [types.InlineKeyboardButton(text="КОМАНДЫ", callback_data="com"),
               types.InlineKeyboardButton(text="ИВЕНТЫ", callback_data="even"),
               types.InlineKeyboardButton(text="АВТОР", callback_data="auth"),
               types.InlineKeyboardButton(text="ФУНКЦИИ", callback_data="fun")]

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)

    try:
        await bot.send_voice(chat_id=message.chat.id, voice=open('../data/tts.ogg', 'rb'),
                             caption='*-* Этот АБОБОТ поможет вам приятно провести время в чате с различными командами, '
                                     'ивентами и удобными функциями, которые облегчают использование чата)\n\n'
                                     '*-* Также прошу если вам понравился бот, оставить отзыв о его использовании на '
                                     'команду /report)', parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)
    except Exception:
        await bot.send_message(chat_id=message.chat.id,
                               text='*-* Этот АБОБОТ поможет вам приятно провести время в чате с различными командами, '
                                    'ивентами и удобными функциями, которые облегчают использование чата)\n\n'
                                    '*-* Также прошу если вам понравился бот, оставить отзыв о его использовании на '
                                    'команду /report)', parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)


# ИЛАЙН КЛАВИАТУРА HELP
@dp.callback_query_handler(text="auth")
async def author(call: types.CallbackQuery):
    await call.message.answer(text='*| АВТОР |*\n\n*>>* Этот бот, как бы это не печально звучало, но одна из лучших'
                                   ' моих работ и если кого-нибудь у меня получится действительно достойный продукт,'
                                   ' вы сможете о нём узнать в моём телеграм канале *@itsproger*', parse_mode=types.ParseMode.MARKDOWN)


@dp.callback_query_handler(text="fun")
async def function(call: types.CallbackQuery):
    await call.message.answer(text='*| ФУНКЦИИ |*\n\n*1.* Возможность перевода случайно написанного текста на '
                                   'транслите\n*2.* Ведение обширной статистики сообщений\n*3.* Упоминание участника '
                                   'при написании его имени в чате\n*4.* Автоматическое удаление системных сообщений',
                              parse_mode=types.ParseMode.MARKDOWN)


@dp.callback_query_handler(text="com")
async def commands(call: types.CallbackQuery):
    await call.message.answer(text='<b>| КОМАНДЫ |</b>\n\n/all - упомянуть всех в чате\n/help - полный список функций\n'
                                   '/stat_group - полная статистика группы\n/stat_user - полная статистика '
                                   'отправителя\n/edit и /back_edit - первая команда даёт возможность '
                                   'сменить имя для упоминаний на любое слово, а вторая для возврата динамического '
                                   'имени\n/start_bot и /stop_bot - возможность отключения текстовых ивентов',
                              parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(text="even")
async def events(call: types.CallbackQuery):
    await call.message.answer(text='*| ИВЕНТЫ |*\n\n*"Чмокнуть"* - сделать кому-нибудь приятно\n*"Отмудохать"* - '
                                   'выместить злость на кого-нибудь\n*"Число от ... до ..."* - случайное значение из '
                                   'диапозона\n*"Подраться с ..."* - повод кого-нибудь побить\n*"Переведи (..) - ..."* '
                                   '- перевод слова на керпичный язык\n*"Дай блять совет!"* - даёт рандомный охуенный '
                                   'совет\n*"Переверни - ..."* - переворачивает слова в предложении\n*"Озвучь - ..."* '
                                   '- озвучивает написанный текст',
                              parse_mode=types.ParseMode.MARKDOWN)


# ОСТАЛЬНЫЕ КОМАНДЫ
@dp.message_handler(commands=['all'], commands_prefix='@/')
async def every(message: types.Message):
    if message.chat.id < 0:
        upd_stat(message.from_user.id, message.chat.id, 3, message.from_user.first_name, True)
        try:
            await message.reply(notice(du.get_user_id(message.from_user.id), True, du.get_group_id(message.chat.id), message.from_user.id),
                                types.ParseMode.HTML)
        except Exception as e:
            # print(repr(e))
            await message.reply('В группе состоит менее 3х человек, из-за чего команда не работает!')
    else:
        await message.reply('Эта команда предназначена для вызова в чате!')


@dp.message_handler(commands=['stat_group'])
async def stat_group(message: types.Message):
    if message.chat.id < 0:
        upd_stat(message.from_user.id, message.chat.id, 3, message.from_user.first_name, True)
        group_id = du.get_group_id(message.chat.id)

        group = db.stat_group(group_id)
        month = db.month_stat_group(group_id)

        await message.answer(text=f'*| СТАТИСТИКА ГРУППЫ |*\n\n'
                                  f'*>>* В целом сообщений *[ {message.message_id} ]*\n\n'
                                  f'*- За всё время* / *За месяц -*\n'
                                  f'*>>* Сообщений в базе *[ {group[0]} / {month[0]} ]*\n\n'
                                  f'*>* Ответов *- [ {group[1]} / {month[1]} ]*\n'
                                  f'*>* Команд *- [ {group[2]} / {month[2]} ]*\n'
                                  f'*>* Ссылок *- [ {group[3]} / {month[3]} ]*\n'
                                  f'*>* Стикеров *- [ {group[5]} / {month[5]} ]*\n'
                                  f'*>* Медиа файлов *- [ {group[4]} / {month[4] } ]*\n'
                                  f'*>* Голос/Кружочки *- [ {group[6]} / {month[6]} ]*',
                             parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['stat_user'])
async def stat_user(message: types.Message):
    if message.chat.id < 0:
        upd_stat(message.from_user.id, message.chat.id, 3, message.from_user.first_name, True)
        user_id, group_id = du.get_user_id(message.from_user.id), du.get_group_id(message.chat.id)

        group = dg.stat_user(user_id, group_id)
        month = dm.stat_user(user_id, group_id)

        namer = "".join(re.sub(r'[^\w\s]', '', message.from_user.first_name).split())
        name = morph.parse(namer)[0].inflect({"gent"})

        if name is None: name = namer
        else: name = name.word

        await message.answer(text=f'*| СТАТИСТИКА {name.upper()} |*\n\n'
                                  f'*- За всё время* / *За месяц -*\n'
                                  f'*>>* Сообщений в базе *[ {group[0]} / {month[0]} ]*\n\n'
                                  f'*>* Ответов *- [ {group[1]} / {month[1]} ]*\n'
                                  f'*>* Команд *- [ {group[2]} / {month[2]} ]*\n'
                                  f'*>* Ссылок *- [ {group[3]} / {month[3]} ]*\n'
                                  f'*>* Стикеров *- [ {group[5]} / {month[5]} ]*\n'
                                  f'*>* Медиа файлов *- [ {group[4]} / {month[4]} ]*\n'
                                  f'*>* Голос/Кружочки *- [ {group[6]} / {month[6]} ]*',
                             parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['edit'])
async def update(message: types.Message):
    if message.chat.id < 0:
        upd_stat(message.from_user.id, message.chat.id, 3, message.from_user.first_name, True)
        user_id, group_id = du.get_user_id(message.from_user.id), du.get_group_id(message.chat.id)

        text_edit = re.sub(r'[^\w\s]', '', message.text.lower()).split()
        if len(text_edit) == 2:
            name = morph.parse(text_edit[1])[0]

            if name is None: name = text_edit[1]
            else: name = name.normal_form

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


@dp.message_handler(commands=['back_edit'])
async def update_return(message: types.Message):
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


@dp.message_handler(commands=['start_bot'])
async def opening(message: types.Message):
    if message.chat.id < 0:
        upd_stat(message.from_user.id, message.chat.id, 3, message.from_user.first_name, True)

        group_id = du.get_group_id(message.chat.id)
        if db.check_status(group_id):
            await message.answer("У вас уже включены текстовые ивенты!")
        else:
            db.update_status(group_id)
            await message.answer("Текстовые ивенты включены!")


@dp.message_handler(commands=['stop_bot'])
async def closing(message: types.Message):
    if message.chat.id < 0:
        upd_stat(message.from_user.id, message.chat.id, 3, message.from_user.first_name, True)

        group_id = du.get_group_id(message.chat.id)
        if db.check_status(group_id):
            db.update_status(group_id)
            await message.answer("Текстовые ивенты отключены!")
        else:
            await message.answer("У вас уже отключены текстовые ивенты!")


# УДАЛЕНИЕ ПОЛЬЗОВАТЕЛЕЙ АВТОМАТИЧЕСКИ
@dp.message_handler(content_types=["left_chat_member"])
async def delete(message: types.Message):
    if du.user_exists(message.left_chat_member.id):
        user_id, group_id = du.get_user_id(message.left_chat_member.id), du.get_group_id(message.chat.id)

        dg.del_user(group_id, user_id)
        if db.group_exists_month(group_id):
            if dm.user_exists(user_id, group_id): dm.del_user(group_id, user_id)

        try: await message.delete()
        except Exception: return


# УДАЛЕНИЕ ТЕХ. СООБЩЕНИЙ
@dp.message_handler(content_types=["new_chat_title", "new_chat_photo", "pinned_message", "voice_chat_ended",
                                   "voice_chat_participants_invited"])
async def chat_events(message: types.Message):
    try: await message.delete()
    except Exception: return


# СТАТИСТИКА
@dp.message_handler(content_types=['location', 'contact', 'video', 'photo', 'audio', 'document'])
async def media(message: types.Message):
    if message.chat.id < 0: upd_stat(message.from_user.id, message.chat.id, 5, message.from_user.first_name, True)


@dp.message_handler(content_types=['voice', 'video_note'])
async def voice(message: types.Message):
    if message.chat.id < 0: upd_stat(message.from_user.id, message.chat.id, 7, message.from_user.first_name, True)


@dp.message_handler(content_types=['sticker'])
async def stick(message: types.Message):
    if message.chat.id < 0: upd_stat(message.from_user.id, message.chat.id, 6, message.from_user.first_name, True)


# ТЕКСТОВЫЕ ИВЕНТЫ
@dp.message_handler(content_types=['text'])
async def send_events(message: types.Message):
    group_id, user_id, name = message.chat.id, message.from_user.id, message.from_user.first_name

    # ОБНОВЛЕНИЕ КОЛ-ВО
    if message.chat.id < 0:
        upd_stat(user_id, group_id, 1, name)  # СООБЩЕНИЙ
        if len(message.text) > 1 and message.text[0] == '/': upd_stat(user_id, group_id, 3, name)  # КОМАНД
        if 'reply_to_message' in message: upd_stat(user_id, group_id, 2, name)  # ОТВЕТОВ НА СООБЩЕНИЯ

    # ПЕРЕМЕННЫЕ
    low_mes = message.text.lower()  # СООБЩЕНИЕ В НИЖНЕМ РЕГИСТРЕ
    words = message.text.split()  # СПИСОК СЛОВ В СООБЩЕНИИ
    unsigned = re.sub(r'[^\w\s]', '', low_mes).split()  # СПИСОК СЛОВ БЕЗ ПУНКТУАЦИИ
    first_form = [morph.parse(i)[0].normal_form for i in unsigned]  # СПИСОК СЛОВ В ПЕРВОЙ ФОРМЕ
    if message.chat.id < 0:  # СПИСОК ИМЕН В СООБЩЕНИИ (ТОЛЬКО В ГРУППЕ)
        names = [_ for _ in first_form if _ in list(map(lambda x: x[0], dg.all_names(du.get_group_id(group_id))))]

    if len(words) >= 2:
        # ПОЛЕЗНЫЕ ФУНКЦИИ
        if len(words) == 5 and "число от" in low_mes:
            await message.answer(
                text=f"Число <b>[ {random.randint(int(low_mes.split()[2]), int(low_mes.split()[4]))} ]</b>",
                parse_mode=types.ParseMode.HTML)
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
            await bot.send_voice(chat_id=group_id, voice=open('../data/voices/voice.ogg', 'rb'),
                                 caption=f"<b>{text_to_voice}</b>", parse_mode=types.ParseMode.HTML)
            os.remove('../data/voices/voice.ogg')
            return

        # РАНДОМ ИВЕНТЫ
        if "подраться" == words[0].lower() and "с" == words[1].lower():
            text = " ".join([words[i] for i in range(len(words)) if i > 1])

            if random.randint(0, 1) == 0:
                await message.bot.send_photo(chat_id=group_id,
                                             photo=open(f"../data/fight/({random.randint(1, 8)}).jpg", 'rb'),
                                             caption=f"{message.from_user.first_name}, ты был унижен {text.title()}"
                                                     f", с помощью {base.VAR_LOSE[random.randint(0, 3)]}")
            else:
                await message.bot.send_photo(chat_id=group_id,
                                             photo=open(f"../data/fight/({random.randint(1, 8)}).jpg", 'rb'),
                                             caption=f"{message.from_user.first_name}, ты победил в драке "
                                                     f"с {text.title()}, {base.VAR_WIN[random.randint(0, 1)]}")

        # ИВЕНТ ВЗАИМОДЕЙСТВИЯ
        for word in base.TMOK_LIST:
            if word in low_mes:
                lst = [words[i] for i in range(len(words)) if i != 0]
                text = " ".join(lst)

                slv = morph.parse(words[0].lower())[0]
                await message.bot.send_photo(chat_id=group_id,
                                             photo=open(f"../data/tmok/({random.randint(1, 4)}).jpg", 'rb'),
                                             caption=f"{message.from_user.first_name} "
                                                     f"{slv.inflect({'past', 'sing', 'indc'}).word} {text}")

        for word in base.KILL_LIST:
            if word in low_mes:
                lst = [words[i] for i in range(len(words)) if i != 0]
                text = " ".join(lst)

                slv = morph.parse(words[0].lower())[0]
                await message.bot.send_photo(chat_id=group_id,
                                             photo=open(f"../data/kill/({random.randint(1, 6)}).jpg", 'rb'),
                                             caption=f"{message.from_user.first_name} "
                                                     f"{slv.inflect({'past', 'sing', 'indc'}).word} {text}")

        if unsigned[0] in base.QUAT_LIST[0] and \
                unsigned[1] in base.QUAT_LIST[1] and unsigned[2] in base.QUAT_LIST[2]:
            word = requests.get('http://fucking-great-advice.ru/api/random').json()
            await message.reply(word["text"])
            return

    if message.chat.id < 0:
        # ЛИСТ КОМАНДЫ
        if names:
            try:
                await message.reply(notice(names, False, du.get_group_id(group_id), user_id), types.ParseMode.HTML)
            except Exception as e:
                return
                """
                await bot.send_message(chat_id=base.TEX_GROUP, text=f"<b>[ {str(dt.now())[:-10]} ]</b> "
                                                                    f"<b><i>=></i></b> <i>{repr(e)}</i> (уведомления по именам)",
                                       parse_mode=types.ParseMode.HTML)
                """
            return

        # ПЕРЕВОДЧИК СЛОВ
        if checker([i for i in low_mes], words, group_id, user_id, name.lower()) == len(low_mes) and \
                not any([engl_dict.check(i) for i in unsigned]):
            await message.reply(f"[{message.from_user.first_name}](tg://user_id?id={user_id}) *>* {translator(words)}",
                                types.ParseMode.MARKDOWN)
            return


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    executor.start_polling(dp, skip_updates=True)
