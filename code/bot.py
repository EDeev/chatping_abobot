import asyncio
import logging

from init import bot, dp
from handlers import router


async def main() -> None:
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), skip_updates=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    try:  asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
        pass