import asyncio
from aiogram import Bot, Dispatcher

from app.handlers import router, set_bot_instance, notes_storage
from app import reminders


async def main():
    bot = Bot(token='8373689721:AAFwDs9bTld4UkUyhqUfU-CPf2fgPFBcRqs')
    dp = Dispatcher()
    dp.include_router(router)
    
    set_bot_instance(bot)
    reminders.start_reminder_checker(notes_storage, bot)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')