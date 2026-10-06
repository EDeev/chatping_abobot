import asyncio
import logging
from datetime import date

from init import bot, dp, db, dm
from handlers import router


def reset_month_if_needed(today=None):
    """Статистика «за месяц» раньше нигде не обнулялась и копилась с момента создания таблиц.
    При первом запуске месяц только запоминается — обнуление со следующей смены месяца"""
    key = (today or date.today()).strftime("%Y-%m")
    saved = db.get_meta("month")
    if saved == key:
        return False
    if saved is not None:
        db.reset_month()
        dm.reset_all()
        logging.info("Месячная статистика обнулена: %s → %s", saved, key)
    db.set_meta("month", key)
    return saved is not None


async def month_watcher():
    while True:
        try:
            reset_month_if_needed()
        except Exception:
            logging.exception("Не удалось обнулить месячную статистику")
        await asyncio.sleep(600)


async def main() -> None:
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    watcher = asyncio.create_task(month_watcher())
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        watcher.cancel()


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    try:  asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")
        pass