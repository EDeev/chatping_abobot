from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.bot import DefaultBotProperties


import base, enchant, pymorphy3

bot = Bot(token=base.TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))
dp = Dispatcher(storage=MemoryStorage())

morph = pymorphy3.MorphAnalyzer()
engl_dict = enchant.Dict("en_US")


import sql

db = sql.Base('../db/base.db')
du = sql.User('../db/users.db')
dg = sql.Group('../db/groups.db')
dm = sql.Month('../db/month.db')