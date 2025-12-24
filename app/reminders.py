from datetime import datetime
from aiogram import Bot
import asyncio

notes_storage = None
bot_instance = None


async def check_reminders():
    while True:
        try:
            if notes_storage and bot_instance:
                current_time = datetime.now()
                
                for user_id, notes_list in notes_storage.items():
                    for note in notes_list:
                        if note.get('reminder_time') and not note.get('reminder_sent', False):
                            try:
                                reminder_time = datetime.fromisoformat(note['reminder_time'])
                                
                                if current_time >= reminder_time:
                                    await bot_instance.send_message(
                                        user_id,
                                        f'Напоминание!\n\n{note["text"]}'
                                    )
                                    note['reminder_sent'] = True
                            except Exception as e:
                                print(f'Ошибка при отправке напоминания: {e}')
                
                await asyncio.sleep(10)
            else:
                await asyncio.sleep(5)
        except Exception as e:
            print(f'Ошибка в check_reminders: {e}')
            await asyncio.sleep(5)


def start_reminder_checker(storage, bot):
    global notes_storage, bot_instance
    notes_storage = storage
    bot_instance = bot
    asyncio.create_task(check_reminders())

