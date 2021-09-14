import logging, random, pymorphy2, requests, asyncio, emoji, base, re

from sql import SQLighter
from datetime import datetime
from script import cheker, translator, notice, lang_form, times, autozak, update_stat, revers
from aiogram import Bot, Dispatcher, executor, types

# log level
logging.basicConfig(level=logging.INFO)

# bot init
bot = Bot(token=base.TOKEN)
dp = Dispatcher(bot)
morph = pymorphy2.MorphAnalyzer()

# инициализируем соединение с БД
db = SQLighter('groups.db')


# events
@dp.message_handler(content_types=["new_chat_members"])
async def notification(message: types.Message):
    if not db.group_exists(message.chat.id):
        db.add_group(message.chat.id)
        db.add_month_group(message.chat.id)
        db.created_group(message.chat.id)
        await bot.send_message(message.chat.id, f'ID <b>[ {message.chat.id} ]</b>\n\nДля того, чтобы уведомления по '
                                                f'имени и команда /all нормально функционировали, необходимо чтобы '
                                                f'каждый участник группы написал хотя бы одно сообщение в чат! Также '
                                                f'для того, чтобы системные сообщения удалялись автоматически, '
                                                f'необходимо боту выдать права администратора!', types.ParseMode.HTML)
    else:
        try:
            await message.delete()
        except Exception:
            print(f'{message.chat.title} >>> НЕ УДАЛОСЬ УДАЛИТЬ СООБЩЕНИЕ')


@dp.message_handler(commands=['start'])
async def helps(message: types.Message):
    if message.chat.id > 0:
        id_group, user = message.chat.id, message.from_user.id
        name_db = re.sub(r'[^\w\s]', '', message.from_user.first_name.lower())
        try:
            if not db.user_exists(user, id_group):
                db.add_user(user, name_db, id_group)
            else:
                if user in db.get_users(id_group):
                    db.update_name(user, name_db, id_group)
        except Exception as e:
            await message.answer("Вы запустили бота в личном чате! Для работы в группе или в общем чате нечего делать "
                                 "не надо, лишь добавить в чат и выдать права на удаление сообщений в чате!\n\n- Для "
                                 "введения в обширный функционал бота можете воспользоваться командой /help!")
            db.add_group(id_group)
            db.add_month_group(id_group)
            db.created_group(id_group)
            db.add_user(user, name_db, id_group)
    else:
        return


@dp.message_handler(commands=['help'])
async def helps(message: types.Message):
    update_stat(3, message, True)

    buttons = [types.InlineKeyboardButton(text="КОМАНДЫ", callback_data="com"),
               types.InlineKeyboardButton(text="ИВЕНТЫ", callback_data="even"),
               types.InlineKeyboardButton(text="ОШИБКИ", callback_data="err"),
               types.InlineKeyboardButton(text="АВТОР", callback_data="auth"),
               types.InlineKeyboardButton(text="ФУНКЦИИ", callback_data="fun")]
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)

    await bot.send_voice(chat_id=message.chat.id, voice=open('data/tts.ogg', 'rb'),
                         caption='*-* Этот АБОБОТ поможет вам приятно провести время в чате с различными командами, '
                                 'ивентами и удобными функциями, которые облегчают использование чата)\n\n'
                                 '*-* Также прошу если вам понравился бот, оставить отзыв о его использовании на '
                                 'команду /report)', parse_mode=types.ParseMode.MARKDOWN, reply_markup=keyboard)


# ИЛАЙН КЛАВИАТУРА HELP
@dp.callback_query_handler(text="err")
async def error(call: types.CallbackQuery):
    await call.message.answer(text='*| ОШИБКИ |*\n\n*-* Так как бот разрабатывается одним человеком, все баги и '
                                   'недочёты програмы выявить сразу очень трудно, поэтому я буду признателен вам если '
                                   'о найденых ошибка вы сообщите по команде /report\n\n*>* Отправить в формате '
                                   '*[ /report {сообщение} ]*', parse_mode=types.ParseMode.MARKDOWN)


@dp.callback_query_handler(text="auth")
async def function(call: types.CallbackQuery):
    await call.message.answer(text='*| АВТОР |*\n\n*>>* Официальный телеграмм канал автора *@govnacoder*\n\n*-* Я '
                                   'практикуюсь в програмировании разрабатывая ботов и простенькие приложения, если '
                                   'интерестно ознокомиться с моими работами, то переходити ко мне в телеграм канал!',
                              parse_mode=types.ParseMode.MARKDOWN)


@dp.callback_query_handler(text="fun")
async def function(call: types.CallbackQuery):
    await call.message.answer(text='*| ФУНКЦИИ |*\n\n*1.* Возможность перевода случайно написанного текста на '
                                   'транслите\n*2.* Ведение обширной статистики сообщений\n*3.* Упоминание участника '
                                   'при написании его имени в чате\n*4.* Автоматическое удаление системных сообщений',
                              parse_mode=types.ParseMode.MARKDOWN)


@dp.callback_query_handler(text="com")
async def commands(call: types.CallbackQuery):
    await call.message.answer(text='<b>| КОМАНДЫ |</b>\n\n/all - упомянуть всех в чате\n/vote - напишите в начале '
                                   'сообщения и создасться простой опрос (Да / Нет)\n/report - жалобы и '
                                   'предложения\n/help - полный список функций\n/statistic_group - полная статистика '
                                   'группы\n/statistic_user - полная статистика отправителя\n/srednya_statistic - '
                                   'средняя статистика группы\n/edit и /back_edit - первая команда даёт возможность '
                                   'сменить имя для упоминаний на любое слово, а вторая для возврата динамического '
                                   'имени\n/start_bot и /stop_bot - возможность отключения текстовых ивентов\n/like '
                                   'и /dislike - даёт возможность оценить то или иное сообщение пользователя',
                              parse_mode=types.ParseMode.HTML)


@dp.callback_query_handler(text="even")
async def events(call: types.CallbackQuery):
    await call.message.answer(text='*| ИВЕНТЫ |*\n\n*"Чмокнуть"* - сделать кому-нибудь приятно\n*"Отмудохать"* - '
                                   'выместить злость на кого-нибудь\n*"Число от ... до ..."* - случайное значение из '
                                   'диапозона\n*"Подраться с ..."* - повод кого-нибудь побить\n*"Переведи (..) - ..."* '
                                   '- перевод слова на керпичный язык\n*"Дай блять совет!"* - даёт рандомный охуенный '
                                   'совет\n*"Переверни - ..."* - переворачивает слова в предложении',
                              parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['all'], commands_prefix='@/')
async def always(message: types.Message):
    update_stat(3, message, True)
    try:
        await message.reply(notice(message.from_user.first_name, True, message.chat.id, message.from_user.id),
                            types.ParseMode.HTML)
    except Exception:
        await message.reply('В группе состоит менее 3х человек, из-за чего команда не работает!')


@dp.message_handler(commands=['report'])
async def answer(message: types.Message):
    update_stat(3, message, True)
    if len(message.text.split()) > 1:
        await bot.send_message(chat_id='-1001510980656',
                               text=f'{message.chat.title} >> '
                                    f'[{message.from_user.first_name}](tg://user?id={message.from_user.id}) '
                                    f'> {message.text}', parse_mode=types.ParseMode.MARKDOWN)
        await message.answer("Ваше сообщение передано администратору)")
    else:
        await message.answer("Заполнять обращение к администратору надо по форме */report { жалоба или предложение }*",
                             types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['statistic_group'])
async def stat(message: types.Message):
    update_stat(3, message, True)
    group = db.stat_element_group(message.chat.id)
    month = db.stat_element_month_group(message.chat.id)

    try:
        await message.answer(text=f'*| СТАТИСТИКА ГРУППЫ |*\n\n*>>* В целом сообщений *[ {message.message_id} ]*\n*>>* '
                                  f'Сообщений в базе *[ {group[0]} ]*\n*>>* Среднее количество сообщений в месяц - *[ '
                                  f'{month[0] // group[8]} ]*\n\n*👍* Лайков *[ {group[10]} ]* / *👎* Дизлайков *[ '
                                  f'{group[9]} ]*\n\n*>* Команд *[ {group[2]} ]*\n*>* Ссылок *[ '
                                  f'{group[3]} ]*\n*>* Стикеров *[ {group[6]} ]*\n*>* Тик-токов *[ {group[4]} ]*\n*>* Медиа'
                                  f' файлов *[ {group[5]} ]*\n*>* Ответов на сообщения *[ {group[1]} ]*\n*>* Голос / Видео '
                                  f'сообщений *[ {group[7]} ]*', parse_mode=types.ParseMode.MARKDOWN)
    except Exception:
        await message.answer(text=f'*| СТАТИСТИКА ГРУППЫ |*\n\n*>>* В целом сообщений *[ {message.message_id} ]*\n*>>* '
                                  f'Сообщений в базе *[ {group[0]} ]*\n\n*👍* Лайков *[ {group[10]} ]* / *👎* Дизлайков *[ '
                                  f'{group[9]} ]*\n\n*>* Команд *[ {group[2]} ]*\n*>* Ссылок *[ '
                                  f'{group[3]} ]*\n*>* Стикеров *[ {group[6]} ]*\n*>* Тик-токов *[ {group[4]} ]*\n*>* Медиа'
                                  f' файлов *[ {group[5]} ]*\n*>* Ответов на сообщения *[ {group[1]} ]*\n*>* Голос / Видео '
                                  f'сообщений *[ {group[7]} ]*', parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['statistic_user'])
async def stat(message: types.Message):
    update_stat(3, message, True)
    user = db.stat_element_user(message.from_user.id, message.chat.id)
    try:
        name = morph.parse(db.get_name_user(message.from_user.id, message.chat.id))[0]
        name = name.inflect({"gent"}).word.upper()
    except Exception:
        name = message.from_user.first_name.lower().upper()

    try:
        err = 1 // user[8]
        await message.answer(text=f'*| СТАТИСТИКА {name} |*\n\n*>>* Всего сообщений *[ '
                                  f'{user[0]} ]*\n*>>* Среднее количество сообщений в месяц - *[ {user[0] // user[8]} '
                                  f']*\n\n*👍* Лайков *[ {user[10]} ]* / *👎* Дизлайков *[ {user[9]} ]*\n\n*>* Команд *[ '
                                  f'{user[2]} ]*\n*>* Ссылок *[ {user[3]} ]*\n*>* Стикеров '
                                  f'*[ {user[6]} ]*\n*>* Тик-токов *[ {user[4]} ]*\n*>* Медиа файлов *[ {user[5]} ]*\n*>* '
                                  f'Ответов на сообщения *[ {user[1]} ]*\n*>* Голос / Видео сообщений *[ {user[7]} ]*',
                             parse_mode=types.ParseMode.MARKDOWN)
    except Exception:
        await message.answer(text=f'*| СТАТИСТИКА {name} |*\n\n*>>* Всего сообщений *[ '
                                  f'{user[0]} ]*\n\n*👍* Лайков *[ {user[10]} ]* / *👎* Дизлайков *[ {user[9]} ]*\n\n*>* '
                                  f'Команд *[ {user[2]} ]*\n*>* Ссылок *[ {user[3]} ]*\n*>* Стикеров '
                                  f'*[ {user[6]} ]*\n*>* Тик-токов *[ {user[4]} ]*\n*>* Медиа файлов *[ {user[5]} ]*\n*>* '
                                  f'Ответов на сообщения *[ {user[1]} ]*\n*>* Голос / Видео сообщений *[ {user[7]} ]*',
                             parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['srednya_statistic'])
async def stat(message: types.Message):
    update_stat(3, message, True)
    timer = db.stat_element_group(message.chat.id)[8]
    month = db.stat_element_month_group(message.chat.id)

    try:
	    if timer != 0:
	        await message.answer(text=f'*| СРЕДНЯЯ СТАТИСТИКА ГРУППЫ |*\n\n*>>* Среднее количество сообщений в месяц - '
	                                  f'*[ {month[0] // timer} ]*\n\n*👍* Лайков *[ {month[9] // timer} ]* / *👎* Дизлайков *[ {month[8] // timer} '
	                                  f']*\n\n*>* Команд *[ {month[2] // timer} ]*\n*>* Ссылок *[ {month[3] // timer} ]*\n*>* Стикеров '
	                                  f'*[ {month[6] // timer} ]*\n*>* Тик-токов *[ {month[4] // timer} ]*\n*>* Медиа файлов *[ {month[5] // timer} ]*\n*>* '
	                                  f'Ответов на сообщения *[ {month[1] // timer} ]*\n*>* Голос / Видео сообщений *[ {month[7] // timer} ]*',
	                             parse_mode=types.ParseMode.MARKDOWN)
	    else:
	        await message.reply('Статистика не может быть показана, так как с момента добавления бота прошло менее месяца!')
    except Exception:
        await message.reply('Вывод стаистики произвёл ошибку, вероятнее всего в вашем чате были использованы не все виды сообщений!')


# ЕЖЕМЕСЕЧНОЕ УВЕДОМЛЕНИЕ
async def time(wait_for):
    while True:
        await asyncio.sleep(wait_for)

        file = open('month.txt', 'r')
        data = file.readline()
        file.close()

        month = datetime.now().date().month
        day = datetime.now().date().day
        if int(data) != int(month):
            for group in db.all_id_group_lst():
                last = db.month_stat_group(group)
                await bot.send_message(chat_id=group,
                                       text=f'*| СТАТИСТИКА ГРУППЫ ЗА ПРОШЕДШИЙ МЕСЯЦ |*\n\n*>>* В целом сообщений *[ '
                                            f'{last[0]} ]*\n\n*👍* Лайков *[ {last[9]} ]* / *👎* Дизлайков *[ '
                                            f'{last[8]} ]*\n\n*>* Команд *[ {last[2]} ]*\n*>* Ссылок *[ {last[3]} '
                                            f']*\n*>* Стикеров *[ {last[6]} ]*\n*>* Тик-токов *[ {last[4]} ]*\n*>* '
                                            f'Медиа файлов *[ {last[5]} ]*\n*>* Ответов на сообщения *[ {last[1]} '
                                            f']*\n*>* Голос / Видео сообщений *[ {last[7]} ]*',
                                       parse_mode=types.ParseMode.MARKDOWN)
                db.statistics_group(group, 0)
                for user in db.id_lst(group):
                    db.user_statistic(user, group, 0)
                    
            file = open('month.txt', 'w')
            file.write(str(month))
            file.close()
        elif (month == 6) and (day == 28):
            for group in db.all_id_group_lst():
                await bot.send_message(chat_id=group,
                                       text=f'Уряяя! У меня сегодня день рождения!',
                                       parse_mode=types.ParseMode.MARKDOWN)


@dp.message_handler(commands=['like'])
async def like(message: types.Message):
    update_stat(3, message, True)
    if message.reply_to_message:
        update_stat(2, message)
        love = (message.reply_to_message.from_user.id == message.from_user.id)
        try:
            comm = (message.reply_to_message.text[0] == '/')
        except Exception:
            comm = False
        if love is False and comm is False:
            db.statistics_group(message.chat.id, 10)
            db.user_statistic(message.reply_to_message.from_user.id, message.chat.id, 10)
            try:
                await message.delete()
            except Exception:
                pass
            await bot.send_message(chat_id=message.chat.id, text=emoji.emojize(':thumbs_up:'),
                                   reply_to_message_id=message.reply_to_message.message_id)

        else:
            if love:
                await message.answer('Ай-яй-яй! За себя голосовать не хорошо!')
            elif comm:
                await message.answer('Оценивать команду не рационально!')
    else:
        await message.answer('Команда должна быть ответом на сообщение пользователя!')


@dp.message_handler(commands=['dislike'])
async def dislike(message: types.Message):
    update_stat(3, message, True)
    if message.reply_to_message:
        update_stat(2, message)
        love = (message.reply_to_message.from_user.id == message.from_user.id)
        try:
            comm = (message.reply_to_message.text[0] == '/')
        except Exception:
            comm = False
        if love is False and comm is False:
            db.statistics_group(message.chat.id, 9)
            print(">>", message.from_user.first_name, datetime.now())
            db.user_statistic(message.reply_to_message.from_user.id, message.chat.id, 9)
            try:
                await message.delete()
            except Exception:
                pass
            await bot.send_message(chat_id=message.chat.id, text=emoji.emojize(':thumbs_down:'),
                                   reply_to_message_id=message.reply_to_message.message_id)

        else:
            if love:
                await message.answer('Ай-яй-яй! За себя голосовать не хорошо!')
            elif comm:
                await message.answer('Оценивать команду не рационально!')
    else:
        await message.answer('Команда должна быть ответом на сообщение пользователя!')


@dp.message_handler(commands=['edit'])
async def update(message: types.Message):
    update_stat(3, message, True)
    text_edit = re.sub(r'[^\w\s]', '', message.text.lower()).split()
    if len(text_edit) == 2:
        db.edit_name(message.from_user.id, text_edit[1], message.chat.id, 1)
        name_edit = db.name_lst(message.chat.id)[db.id_lst(message.chat.id).index(str(message.from_user.id))]
        await message.reply(f'{name_edit.title()}, ваше имя было успешно изменено)')
    else:
        await message.reply(f'Вы не правильно ввели имя! Имя должно быть из одного слова и идти сразу после команды!')


@dp.message_handler(commands=['back_edit'])
async def update_return(message: types.Message):
    update_stat(3, message, True)
    text_name = re.sub(r'[^\w\s]', '', message.from_user.first_name.lower())
    db.edit_name(message.from_user.id, text_name, message.chat.id, 0)
    await message.reply(f'{text_name.title()}, вы успешно вернулись к динамическому изменению имени)')


@dp.message_handler(commands=['vote'])
async def voting(message: types.Message):
    update_stat(3, message, True)
    await bot.send_poll(chat_id=message.chat.id, question="Итак, что вы выберите?",
                        options=['Да', 'Нет'], is_anonymous=False, open_period=600,
                        reply_to_message_id=message.message_id)


@dp.message_handler(commands=['start_bot'])
async def opening(message: types.Message):
    update_stat(3, message, True)
    if not db.group_exists(message.chat.id):
        db.add_group(message.chat.id)
        await message.answer(
            "Ваша группа изменила свой статус, из-за чего данные о пользователях были стёрты, "
            "вам надо снова отправить хотя бы по одному сообщению от каждого пользователя! Текстовые ивенты включены!")
    else:
        for group in db.get_group():
            if str(group[1]) == str(message.chat.id):
                await message.answer("У вас уже включены текстовые ивенты!")
                break
        else:
            db.update_status_group(message.chat.id, True)
            await message.answer("Текстовые ивенты включены!")


@dp.message_handler(commands=['stop_bot'])
async def closing(message: types.Message):
    update_stat(3, message, True)
    if not db.group_exists(message.chat.id):
        db.add_group(message.chat.id, False)
        await message.answer(
            "Ваша группа изменила свой статус, из-за чего данные о пользователях были стёрты, "
            "вам надо снова отправить хотя бы по одному сообщению от каждого пользователя! Текстовые ивенты отключены!")
    else:
        for group in db.get_group():
            if str(group[1]) == str(message.chat.id):
                db.update_status_group(message.chat.id, False)
                await message.answer("Текстовые ивенты отключены!")
                break
        else:
            await message.answer("У вас уже отключены текстовые ивенты!")


@dp.message_handler(
    content_types=["migrate_to_chat_id", "migrate_from_chat_id", "new_chat_title", "new_chat_photo", "pinned_message", 
                   "voice_chat_scheduled", "voice_chat_started", "voice_chat_ended", "voice_chat_participants_invited",
                   "left_chat_member"])
async def chat_events(message: types.Message):
    try:
        await message.delete()
    except Exception:
        print(f'{message.chat.title} >>> НЕ УДАЛОСЬ УДАЛИТЬ СООБЩЕНИЕ')


# СТАТИСТИКА
@dp.message_handler(content_types=['location', 'contact', 'video', 'photo', 'audio', 'document'])
async def media(message: types.Message):
    update_stat(6, message, True)


@dp.message_handler(content_types=['voice', 'video_note'])
async def mms(message: types.Message):
    update_stat(8, message, True)


@dp.message_handler(content_types=['sticker'])
async def stick(message: types.Message):
    update_stat(7, message, True)


# ТЕКСТОВЫЕ ИВЕНТЫ
@dp.message_handler(content_types=['text'])
async def send_events(message: types.Message):
    id_group, name_group, user = message.chat.id, message.chat.title, message.from_user.id
    name_db = re.sub(r'[^\w\s]', '', message.from_user.first_name.lower())
    txt = message.text.lower()     # СООБЩЕНИЕ В НИЖНЕМ РЕГИСТРЕ
    bk = [i for i in txt]          # СПИСОК СИМВОЛОВ СООБЩЕНИЯ

    # ПРОВЕРКА ПОЛЬЗОВАТЕЛЯ
    try:
        if not db.user_exists(user, id_group):
            db.add_user(user, name_db, id_group)
        else:
            if user in db.get_users(id_group):
                db.update_name(user, name_db, id_group)
    except Exception as e:
        await message.answer(f'<b>Ваша группа [ {name_group} ] изменила свой статус на супергруппу! '
                             f'Из-за этого, список участников был стёрт, и вам необходимо заново отослать '
                             f'хотя бы одно сообщение, для коректного упоминания!</b>', types.ParseMode.HTML)
        db.add_group(id_group)
        db.add_month_group(id_group)
        db.created_group(id_group)
        db.add_user(user, name_db, id_group)

    # ОБНОВЛЕНИЕ КОЛ-ВО СООБЩЕНИЙ
    update_stat(1, message)

    # ОБНОВЛЕНИЕ КОЛ-ВО КОМАНД
    if len(message.text) > 1 and message.text[0] == '/':
        update_stat(3, message)

    # ОБНОВЛЕНИЕ КОЛ-ВО ОТВЕТОВ НА СООБЩЕНИЯ
    try:
        if int(message.reply_to_message.message_id) > 1:
            update_stat(2, message)
    except Exception:
        pass

    # ИВЕНТЫ
    if str(message.chat.id) in db.id_group_lst():

        # ПЕРЕМЕННЫЕ
        original = message.text.split()                                 # СПИСОК СЛОВ В СООБЩЕНИИ
        no_pct = re.sub(r'[^\w\s]', '', txt)                            # СООБЩЕНИЕ БЕЗ ПУНКТУАЦИИ
        norm = [morph.parse(i)[0].normal_form for i in no_pct.split()]  # СПИСОК СЛОВ В ПЕРВОЙ ФОРМЕ
        names = [_ for _ in norm if _ in db.name_lst(message.chat.id)]  # СПИСОК ИМЕН В СООБЩЕНИИ

        # ПОЛЕЗНЫЕ ФУНКЦИИ
        if len(original) == 5 and "число от" in txt:
            await message.answer(text=f"Число <b>[ {random.randint(int(txt.split()[2]), int(txt.split()[4]))} ]</b>",
                                 parse_mode=types.ParseMode.HTML)
            return

        if len(original) > 1 and no_pct.split()[0] == 'переведи':
            if "переведи - " in txt:
                await message.answer(lang_form([original[_] for _ in range(len(original)) if _ > 1]))
            elif f"переведи ({no_pct.split()[1]}) - " in txt:
                if len(no_pct.split()[1]) == 1:
                    await message.answer(lang_form([original[_] for _ in range(len(original)) if _ > 2],
                                                   no_pct.split()[1]))
            return

        if len(original) > 1 and no_pct.split()[0] == 'переверни':
            if "переверни - " in txt:
                await message.answer(revers(message.text[12:], True))
            elif "переверни полностью - " in txt:
                await message.answer(revers(message.text[22:], False))
            return

        # РАНДОМ ИВЕНТЫ
        if len(original) >= 2:
            if "подраться с" in txt:
                text = " ".join([original[i] for i in range(len(original)) if i > 1])

                if random.randint(0, 1) == 0:
                    await message.bot.send_photo(chat_id=id_group,
                                                 photo=open(f"data/fight/({random.randint(1, 8)}).jpg", 'rb'),
                                                 caption=f"{message.from_user.first_name} ты был унижен {text.title()}"
                                                         f" с помощью {base.VAR_LOSE[random.randint(0, 3)]}")
                else:
                    await message.bot.send_photo(chat_id=id_group,
                                                 photo=open(f"data/fight/({random.randint(1, 8)}).jpg", 'rb'),
                                                 caption=f"{message.from_user.first_name} ты победил в драке "
                                                         f"с {text.title()}, {base.VAR_WIN[random.randint(0, 1)]}")

        # ИВЕНТ ВЗАИМОДЕЙСТВИЯ
        if len(original) >= 2:
            for word in base.TMOK_LIST:
                if word in txt:
                    lst = [original[i] for i in range(len(original)) if i != 0]
                    text = " ".join(lst)

                    slv = morph.parse(original[0].lower())[0]

                    await message.bot.send_photo(chat_id=id_group,
                                                 photo=open(f"data/tmok/({random.randint(1, 4)}).jpg", 'rb'),
                                                 caption=f"{message.from_user.first_name} "
                                                         f"{slv.inflect({'past', 'sing', 'indc'}).word} {text}")

            for word in base.KILL_LIST:
                if word in txt:
                    lst = [original[i] for i in range(len(original)) if i != 0]
                    text = " ".join(lst)

                    slv = morph.parse(original[0].lower())[0]

                    await message.bot.send_photo(chat_id=id_group,
                                                 photo=open(f"data/kill/({random.randint(1, 6)}).jpg", 'rb'),
                                                 caption=f"{message.from_user.first_name} "
                                                         f"{slv.inflect({'past', 'sing', 'indc'}).word} {text}")
            
            for word_1 in base.QUAT_LIST[0]:
                flag = False
                for word_2 in base.QUAT_LIST[1]:
                    for word_3 in base.QUAT_LIST[2]:
                        if no_pct == " ".join([word_1, word_2, word_3]):
                            word = (requests.get('http://fucking-great-advice.ru/api/random').text).split('"')[5]
                            await message.reply(word)
                            flag = True
                    if flag:
                        break
                if flag:
                    break

        # ЛИСТ КОМАНДЫ
        if names:
            await message.reply(notice(names, False, id_group, message.from_user.id), types.ParseMode.HTML)
            return

        # ПЕРЕВОДЧИК СЛОВ
        if cheker(bk, original, id_group, user) == len(txt):
            await message.reply(f"[{message.from_user.first_name}](tg://user?id={user}) *>* {translator(original)}", 
                                types.ParseMode.MARKDOWN)
            return


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(time(21600)) # КАЖДЫЕ 6 ЧАСОВ ПРОВЕРКА
    executor.start_polling(dp, skip_updates=True)
