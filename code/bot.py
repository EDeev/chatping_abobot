import asyncio
import logging
import traceback

from aiogram import Bot, Dispatcher
from aiogram.client.bot import DefaultBotProperties
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import ErrorEvent

import config
import db
from handlers import routers
from handlers.chat import check_all

CHECK_INTERVAL = 6 * 3600  # сверка статуса бота в чатах


def create_dispatcher():
    dp = Dispatcher(storage=MemoryStorage())
    for router in routers:
        dp.include_router(router)

    @dp.errors()
    async def on_error(event: ErrorEvent, bot: Bot):
        """Ошибка обработчика — в лог и в технический чат"""
        logging.exception("Ошибка обработки", exc_info=event.exception)
        if config.DEBUG_CHAT_ID:
            tb = "".join(traceback.format_exception(event.exception))[-3500:]
            try:
                await bot.send_message(config.DEBUG_CHAT_ID, f"<b>AboBot: ошибка</b>\n<pre>{tb.replace('<', '&lt;')}</pre>")
            except Exception:
                pass
        return True

    return dp


async def periodic_check(bot: Bot):
    while True:
        try:
            await check_all(bot)
        except Exception:
            logging.exception("Сверка статуса бота в чатах")
        await asyncio.sleep(CHECK_INTERVAL)


async def main() -> None:
    bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await db.connect(config.DATABASE_URL)
    dp = create_dispatcher()
    await bot.delete_webhook(drop_pending_updates=True)
    checker = asyncio.create_task(periodic_check(bot))
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        checker.cancel()
        await db.close()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
