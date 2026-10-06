import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "XXXXXXXXXX")  # @chat_abobot
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://abobot:abobot@localhost:5432/abobot")
DEBUG_CHAT_ID = os.getenv("DEBUG_CHAT_ID", "")  # технический чат для ошибок

BIG_CHAT = 100            # с какого числа участников действуют ограничения
ALL_COOLDOWN = 300        # /all в большом чате — не чаще, с
ALL_ACTIVE_DAYS = 30      # /all в большом чате зовёт тех, кто писал за столько дней
MENTION_COOLDOWN = 60     # упоминание одного человека в большом чате — не чаще, с
