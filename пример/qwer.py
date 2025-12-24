from email import message
import telebot
from telebot import types
import crud.product as product_db
API_TOKEN = '8373689721:AAFwDs9bTld4UkUyhqUfU-CPf2fgPFBcRqs'

bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    product_db.table()


    kb = types.ReplyKeyboardMarkup(row_width=2)
    help_btn = types.KeyboardButton(text="/help")
    add_btn = types.KeyboardButton(text="/addproduct")
    update_btn = types.KeyboardButton(text="/updateproduct")
    del_btn = types.KeyboardButton(text="/deleteproduct")
    view_btn = types.KeyboardButton(text="/viewproducts")
    kb.add(help_btn, add_btn, update_btn, del_btn, view_btn,)

    bot.send_message(message.chat.id, "hello, this is our test shop", reply_markup=kb)

@bot.message_handler(commands=['help'])
def send_welcome(message):
    bot.send_message(message.chat.id, "список моех команд "\
    "\n\n/addproduct - создать продукт"\
    "\n/updateproduct - изменить продукт" \
    "\n/deleteproduct - удалить продукт" \
    "\n/viewproducts - ввывести продукты" 
    )

@bot.message_handler(commands=['addproduct'])
def post_products(message):
    bot.send_message(message.chat.id, "Нaпиши название товара\n\nДля отмены операции напишите \"отмена.\"")
    bot.register_next_step_handler(message, post_product_name)

def post_product_name(message):
    if message.text == "Отмена.":
        bot.send_message(message.chat.id, "Отмена операции")
    else:
        name = message.text 
        product = {}
        product['name'] = name
        bot.send_message(message.chat.id, "НАпишите цену для товара\n\nДля отмены операции напишите \"отмена.\"")
        bot.register_nuxt_step_headler(message, post_product_price, product)

def post_product_price(message, product):
        if message.text == "Отмена.":
            bot.send_message(message.chat.id, "Отмена операции")
        else:
            price = message.text
            if price.isdigit():
                product['price'] = price
                    product_db.create(product)
                    bot.send_message(message.chat.id, "Товар добавлен")

                bot.send_message(message.chat.id, "Цена не в числах")  
            else:
                bot.send_message(message.chat.id, "Цена не задана вчислах\n\nДля отмены операции напишите \"отмена.\"")
                bot.register_nuxt_step_headler(message, post_product_price, product)



@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()





import sqlite3

def table():
    db = sqlite3.connect('shop.db')
    c = db.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS products (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NOT NULL,
              price INTEGER NOT NULL
    )""")
    db.commit()
    db.close()

def create(product):
    db = sqlite3.connect('shop.db')
    c = db.cursor()
    c.execute("INSERT INTO products (name, price) VALUES (?, ?)", (product['name'], product['price']))