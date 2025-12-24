from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, timedelta
import re

import app.keyboards as kb

router = Router()

notes_storage = {}
bot_instance = None


def set_bot_instance(bot: Bot):
    global bot_instance
    bot_instance = bot

class NoteStates(StatesGroup):
    waiting_for_note = State()
    waiting_for_note_time = State()
    waiting_for_delete_id = State()


@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        'Привет! Я бот для заметок.\n\n'
        'Я помогу тебе сохранять и управлять заметками.\n'
        'Используй кнопки ниже или команду /help для помощи.',
        reply_markup=kb.main
    )


@router.message(Command('help'))
async def cmd_help(message: Message):
    help_text = (
        'Справка по использованию бота:\n\n'
        'Добавить заметку - создай новую заметку с возможностью установить напоминание\n'
        'Мои заметки - посмотри все свои заметки\n'
        'Удалить заметку - удали заметку по номеру\n'
        'Удалить все заметки - удали все заметки сразу\n\n'
        'При создании заметки можно установить время напоминания:\n'
        'Формат: ДД.ММ.ГГГГ ЧЧ:ММ (например: 25.12.2024 15:30)\n'
        'Или напиши "пропустить" чтобы сохранить без напоминания\n\n'
        'Команды:\n'
        '/start - начать работу\n'
        '/help - показать эту справку'
    )
    await message.answer(help_text, reply_markup=kb.main)


@router.message(F.text == 'Добавить заметку')
async def add_note_start(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == NoteStates.waiting_for_note or current_state == NoteStates.waiting_for_note_time:
        await state.clear()
    
    await message.answer(
        'Напиши текст заметки:\n\n'
        'После этого можно будет установить время напоминания (или пропустить).'
    )
    await state.set_state(NoteStates.waiting_for_note)


@router.message(F.text == 'Мои заметки')
async def show_notes(message: Message, state: FSMContext):
    current_state = await state.get_state()
    was_cancelled = False
    
    if current_state == NoteStates.waiting_for_note or current_state == NoteStates.waiting_for_note_time:
        await state.clear()
        was_cancelled = True
    
    user_id = message.from_user.id
    
    if user_id not in notes_storage or len(notes_storage[user_id]) == 0:
        if was_cancelled:
            await message.answer('Добавление заметки отменено.\n\nУ тебя пока нет заметок.\n\nИспользуй кнопку "Добавить заметку" для создания.', reply_markup=kb.main)
        else:
            await message.answer('У тебя пока нет заметок.\n\nИспользуй кнопку "Добавить заметку" для создания.', reply_markup=kb.main)
    else:
        if was_cancelled:
            await message.answer('Добавление заметки отменено.')
        
        notes_list = notes_storage[user_id]
        text = 'Твои заметки:\n\n'
        for note in notes_list:
            note_text = f'#{note["id"]}: {note["text"]}'
            if note.get('reminder_time') and not note.get('reminder_sent', False):
                try:
                    reminder_dt = datetime.fromisoformat(note['reminder_time'])
                    time_str = reminder_dt.strftime('%d.%m.%Y %H:%M')
                    note_text += f' (напоминание: {time_str})'
                except:
                    pass
            text += note_text + '\n'
        await message.answer(text, reply_markup=kb.main)


@router.message(F.text == 'Удалить заметку')
async def delete_note_start(message: Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == NoteStates.waiting_for_note or current_state == NoteStates.waiting_for_note_time:
        await state.clear()
        await message.answer('Добавление заметки отменено.')
    
    user_id = message.from_user.id
    
    if user_id not in notes_storage or len(notes_storage[user_id]) == 0:
        await message.answer('У тебя нет заметок для удаления.', reply_markup=kb.main)
        return
    
    notes_list = notes_storage[user_id]
    text = 'Твои заметки:\n\n'
    for note in notes_list:
        note_text = f'#{note["id"]}: {note["text"]}'
        if note.get('reminder_time') and not note.get('reminder_sent', False):
            try:
                reminder_dt = datetime.fromisoformat(note['reminder_time'])
                time_str = reminder_dt.strftime('%d.%m.%Y %H:%M')
                note_text += f' (напоминание: {time_str})'
            except:
                pass
        text += note_text + '\n'
    text += '\nНапиши номер заметки для удаления:'
    
    await message.answer(text)
    await state.set_state(NoteStates.waiting_for_delete_id)


@router.message(F.text == 'Удалить все заметки')
async def delete_all_notes(message: Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == NoteStates.waiting_for_note or current_state == NoteStates.waiting_for_note_time:
        await state.clear()
        await message.answer('Добавление заметки отменено.')
    
    user_id = message.from_user.id
    
    if user_id not in notes_storage or len(notes_storage[user_id]) == 0:
        await message.answer('У тебя нет заметок для удаления.', reply_markup=kb.main)
        return
    
    notes_count = len(notes_storage[user_id])
    notes_storage[user_id] = []
    
    await message.answer(f'Все заметки удалены! Удалено заметок: {notes_count}', reply_markup=kb.main)


@router.message(F.text == 'Помощь')
async def show_help(message: Message, state: FSMContext):
    current_state = await state.get_state()
    
    if current_state == NoteStates.waiting_for_note or current_state == NoteStates.waiting_for_note_time:
        await state.clear()
        await message.answer('Добавление заметки отменено.')
    
    await cmd_help(message)


@router.message(NoteStates.waiting_for_delete_id)
async def delete_note_finish(message: Message, state: FSMContext):
    user_id = message.from_user.id
    
    try:
        note_id = int(message.text)
        notes_list = notes_storage[user_id]
        
        note_found = False
        for i, note in enumerate(notes_list):
            if note['id'] == note_id:
                deleted_text = note['text']
                notes_list.pop(i)
                note_found = True
                
                for j, remaining_note in enumerate(notes_list, start=1):
                    remaining_note['id'] = j
                
                await message.answer(f'Заметка #{note_id} удалена!\n\nТекст: {deleted_text}', reply_markup=kb.main)
                break
        
        if not note_found:
            await message.answer(f'Заметка #{note_id} не найдена. Попробуй еще раз.', reply_markup=kb.main)
        
        await state.clear()
    except ValueError:
        await message.answer('Пожалуйста, введи номер заметки (число).', reply_markup=kb.main)
        await state.clear()


@router.message(NoteStates.waiting_for_note)
async def add_note_text(message: Message, state: FSMContext):
    button_texts = ['Добавить заметку', 'Мои заметки', 'Удалить заметку', 'Удалить все заметки', 'Помощь']
    if message.text in button_texts:
        return
    
    await state.update_data(note_text=message.text)
    await message.answer(
        'Заметка сохранена!\n\n'
        'Хочешь установить время напоминания?\n'
        'Напиши дату и время в формате: ДД.ММ.ГГГГ ЧЧ:ММ\n'
        'Например: 25.12.2024 15:30\n\n'
        'Или напиши "пропустить" чтобы сохранить без напоминания.'
    )
    await state.set_state(NoteStates.waiting_for_note_time)


@router.message(NoteStates.waiting_for_note_time)
async def add_note_time(message: Message, state: FSMContext):
    button_texts = ['Добавить заметку', 'Мои заметки', 'Удалить заметку', 'Удалить все заметки', 'Помощь']
    if message.text in button_texts:
        return
    
    user_id = message.from_user.id
    data = await state.get_data()
    note_text = data.get('note_text')
    
    if user_id not in notes_storage:
        notes_storage[user_id] = []
    
    reminder_time = None
    
    if message.text.lower() in ['пропустить', 'нет', 'без напоминания']:
        reminder_time = None
    else:
        try:
            reminder_time = parse_datetime(message.text)
            if reminder_time <= datetime.now():
                await message.answer(
                    'Время напоминания должно быть в будущем!\n'
                    'Попробуй еще раз или напиши "пропустить".'
                )
                return
        except ValueError:
            await message.answer(
                'Неверный формат времени!\n'
                'Используй формат: ДД.ММ.ГГГГ ЧЧ:ММ\n'
                'Например: 25.12.2024 15:30\n\n'
                'Или напиши "пропустить" чтобы сохранить без напоминания.'
            )
            return
    
    note_id = len(notes_storage[user_id]) + 1
    notes_storage[user_id].append({
        'id': note_id,
        'text': note_text,
        'reminder_time': reminder_time.isoformat() if reminder_time else None,
        'reminder_sent': False
    })
    
    if reminder_time:
        time_str = reminder_time.strftime('%d.%m.%Y %H:%M')
        await message.answer(
            f'Заметка #{note_id} сохранена!\n'
            f'Напоминание установлено на: {time_str}',
            reply_markup=kb.main
        )
    else:
        await message.answer(f'Заметка #{note_id} сохранена!', reply_markup=kb.main)
    
    await state.clear()


def parse_datetime(date_string):
    patterns = [
        r'(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}):(\d{2})',
        r'(\d{1,2})\.(\d{1,2})\.(\d{4})\s+(\d{1,2}):(\d{2}):(\d{2})',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, date_string.strip())
        if match:
            groups = match.groups()
            day, month, year = int(groups[0]), int(groups[1]), int(groups[2])
            hour, minute = int(groups[3]), int(groups[4])
            
            return datetime(year, month, day, hour, minute)
    
    raise ValueError('Неверный формат даты')
