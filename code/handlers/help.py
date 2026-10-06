from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, FSInputFile, InlineKeyboardButton, InlineKeyboardMarkup, Message

from .common import count, in_group
import db

router = Router()

ABOUT = ('<b>-</b> Этот АБОБОТ поможет вам приятно провести время в чате с различными командами, '
         'ивентами и удобными функциями, которые облегчают использование чата)\n\n'
         '<b>-</b> Также прошу если вам понравился бот, оставить отзыв о его использовании на '
         'команду /report)')


@router.message(CommandStart())
@router.message(Command('help'))
async def helps(message: Message):
    await db.ensure_user(message.from_user.id)
    if in_group(message):
        await count(message, 3, 1)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="КОМАНДЫ", callback_data="com"),
         InlineKeyboardButton(text="ИВЕНТЫ", callback_data="even")],
        [InlineKeyboardButton(text="АВТОР", callback_data="auth"),
         InlineKeyboardButton(text="ФУНКЦИИ", callback_data="fun")]
    ])
    try:
        await message.answer_voice(voice=FSInputFile('../data/tts.ogg'), caption=ABOUT, reply_markup=keyboard)
    except Exception:
        await message.answer(ABOUT, reply_markup=keyboard)


@router.callback_query(F.data == "auth")
async def author(call: CallbackQuery):
    await call.message.answer(
        '<b>| АВТОР |</b>\n\n<b>>></b> Этот бот, как бы это не печально звучало, но одна из лучших'
        ' моих работ и если кого-нибудь у меня получится действительно достойный продукт,'
        ' вы сможете о нём узнать в моём телеграм канале <b>@programium</b>')


@router.callback_query(F.data == "fun")
async def function(call: CallbackQuery):
    await call.message.answer(
        '<b>| ФУНКЦИИ |</b>\n\n<b>1.</b> Возможность перевода случайно написанного текста на '
        'транслите\n<b>2.</b> Ведение обширной статистики сообщений\n<b>3.</b> Упоминание участника '
        'при написании его имени в чате\n<b>4.</b> Автоматическое удаление системных сообщений')


@router.callback_query(F.data == "com")
async def commands(call: CallbackQuery):
    await call.message.answer(
        '<b>| КОМАНДЫ |</b>\n\n<b>/all</b> - упомянуть всех в чате\n<b>/help</b> - полный список функций\n'
        '<b>/recognize</b> - транскрипция отмеченного голосового сообщения в текст\n'
        '<b>/stat_group</b> - полная статистика группы\n<b>/stat_user</b> - полная статистика '
        'отправителя\n<b>/top</b> - самые активные участники (<b>/top all</b> - за всё время)\n'
        '<b>/month</b> - итоги месяца (<b>/month 2026-09</b> - за любой месяц)\n'
        '<b>/edit и /back_edit</b> - первая команда даёт возможность '
        'сменить имя для упоминаний на любое слово, а вторая для возврата динамического '
        'имени\n<b>/settings</b> - настройки бота в чате\n'
        '<b>/start_bot и /stop_bot</b> - возможность отключения текстовых ивентов')


@router.callback_query(F.data == "even")
async def events(call: CallbackQuery):
    await call.message.answer(
        '<b>| ИВЕНТЫ |</b>\n\n<b>"Чмокнуть"</b> - сделать кому-нибудь приятно\n<b>"Отмудохать"</b> - '
        'выместить злость на кого-нибудь\n<b>"Число от ... до ..."</b> - случайное значение из '
        'диапозона\n<b>"Подраться с ..."</b> - повод кого-нибудь побить\n<b>"Переведи (..) - ..."</b> '
        '- перевод слова на керпичный язык\n<b>"Дай блять совет!"</b> - даёт рандомный охуенный '
        'совет\n<b>"Переверни - ..."</b> - переворачивает слова в предложении\n<b>"Озвучь - ..."</b> '
        '- озвучивает написанный текст')
