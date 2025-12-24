from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Добавить заметку')],
        [KeyboardButton(text='Мои заметки'), KeyboardButton(text='Удалить заметку')],
        [KeyboardButton(text='Удалить все заметки'), KeyboardButton(text='Помощь')]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите действие'
)
