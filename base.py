# ДАННЫЕ БОТА
TOKEN = "token from BotFather"

# РИКРОЛЛ 
RICKROLL_1 = 'https://vk.cc/8U7VuC' # https://www.youtube.com/watch?v=dQw4w9WgXcQ
RICKROLL_2 = 'https://vk.cc/3A9NI7' # https://youtu.be/dQw4w9WgXcQ

# ОБРАЩЕНИЯ К ПОЛЬЗОВАТЕЛЯМ
KILL_LIST = ["побить", "отмудохать", "избить", "уебать", "отметелить"]
TMOK_LIST = ["поцеловать", "чмокнуть", "соснуть", "лайкнуть"]
QUAT_LIST = [['дай', 'дайте'], ['ахуенный', 'ахуеный', 'охуеный', 'охуенный', 'блять', 'сука'], ['совет', 'совета']]

# ФРАЗЫ ИВЕНТ ДРАКИ
VAR_WIN = ["опустив его ниже плинтуса!", "поставив его на место!"]
VAR_LOSE = ["Кунг - Фу!", "магии!", "резинового члена!", "банды цапель!"]

# ПЕРЕВОДЧИК СЛОВ
ERR = ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p', '[', ']', 'a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l', ';',
       "'", 'z', 'x', 'c', 'v', 'b', 'n', 'm', ',', '.', '/', '`']
ERR_ = ['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P', '{', '}', 'A', 'S', 'D', 'F', 'G', 'H', 'J', 'K', 'L', ':',
        '"', 'Z', 'X', 'C', 'V', 'B', 'N', 'M', '<', '>', '?', '~']
TRU = ['й', 'ц', 'у', 'к', 'е', 'н', 'г', 'ш', 'щ', 'з', 'х', 'ъ', 'ф', 'ы', 'в', 'а', 'п', 'р', 'о', 'л', 'д', 'ж',
       'э', 'я', 'ч', 'с', 'м', 'и', 'т', 'ь', 'б', 'ю', '.']
TRU_ = ['Й', 'Ц', 'У', 'К', 'Е', 'Н', 'Г', 'Ш', 'Щ', 'З', 'Х', 'Ъ', 'Ф', 'Ы', 'В', 'А', 'П', 'Р', 'О', 'Л', 'Д', 'Ж',
        'Э', 'Я', 'Ч', 'С', 'М', 'И', 'Т', 'Ь', 'Б', 'Ю', ',']

ALB = ['а', 'у', 'о', 'ы', 'и', 'э', 'я', 'ю', 'ё', 'е', 'А', 'У', 'О', 'Ы', 'И', 'Э', 'Я', 'Ю', 'Ё', 'Е']



# НА ВСЯКИЙ СЛУЧАЙ

'''
# from filters import IsAdminFilter
    # activate filters
    dp.filters_factory.bind(IsAdminFilter)

# await call.message.answer(str(randint(1, 10)))

# await message.answer_sticker(r'CAACAgIAAxkBAAECmDFg8_fMoE0ZFAYxOh5KRyB2Y7VGZwACfQ0AAtMv4ElQpS-ysl5_6SAE') # ФУГА ДУМАЕТ

# state = dp.current_state(chat=config.GROUP_ID, user=message.from_user.id)
# await state.set_state(User.accepted)

# ОСУЖДАЮ
for word in base.BAN_LIST:
    if word in txt:
        await message.delete()
        await message.answer("ОСУЖДАЮ")
        print(name_group, ">>>", message.text)

for word in base.BAN_NAME:
    if word in txt and not "егор" in txt:
        await message.delete()
        await message.answer("Для обращений существует имя!")
        print(name_group, ">>", message.text)

# бан на минуту
if len(original) == 2:
    if "забанься" in txt:
        await message.bot.restrict_chat_member(chat_id=id_group, user_id=[base.USERS[i][1] for i in base.USERS if i == no_pct.lower().split()[0]][0],
                                               permissions=types.ChatPermissions(),
                                               until_date=int(time()) + (31))
        await message.reply(f'{message.from_user.first_name}, по вашему желанию отлетел дурачок на минуту)')

# админ бан
@dp.message_handler(is_admin=True, commands=['ban'], commands_prefix='!/')
async def ban(message: types.Message):
    if not message.reply_to_message:
        await message.reply("Эта команда должна быть ответом на сообщение!")
        return

    await message.bot.delete_message(config.GROUP_ID, message.message_id)
    await message.bot.kick_chat_member(chat_id=config.GROUP_ID, user_id=message.reply_to_message.from_user.id)

    await message.bot.send_photo(chat_id=config.GROUP_ID, photo="1.jpg", caption="Пользователь унижен!\nПоздравляю ;)")

# чекер данных фото
@dp.message_handler(content_types=['photo'])
async def scan_message(msg: types.Message):
    document_id = msg.photo[0].file_id
    file_info = await bot.get_file(document_id)
    print(f'file_id: {file_info.file_id}')
    print(f'file_path: {file_info.file_path}')
    print(f'file_size: {file_info.file_size}')
    print(f'file_unique_id: {file_info.file_unique_id}')
'''
