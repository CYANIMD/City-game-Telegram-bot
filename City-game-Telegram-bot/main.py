from func import *
import telebot
from telebot import types
import sqlite3 as sql
import random

token = "" # Собственный токен
bot = telebot.TeleBot(token) # Инициализация бота

# Приветствие (запуск бота)
@bot.message_handler(commands=["start", "main"])
def welcome(message):
    add_game(message.chat.id, False)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Да!", callback_data="Yes"),types.InlineKeyboardButton("Нет...", callback_data="No"))
    bot.send_message(message.chat.id, "Привет! Я телеграм бот, с которым можно поиграть \"города\". Опишу правила этой игры:"+
                     "\n(1). Один из игроков называет случайный город;"+
                     "\n(2). Каждый игрок по очереди называет город, который начинается на последнюю букву города (за некоторым исключением), названного предыдущим игроком;"+
                     "\n(3). Нельзя повторять города, которые уже были названы в ходе игры;"+
                     "\n(4). Города должны быть настоящими;"+
                     "\n(5). Если город, названный игроком, заканчивается на букву \"ы\", \"ь\", или \"ъ\", то следующий игрок должен назвать город, начинающийся с предпоследней буквы прошлого города\n" +
                     "Ты готов к игре?", reply_markup=markup)
# Отслеживание нажатия на кнопку
@bot.callback_query_handler(func=lambda call: True)
def event_button(callback):
    match(callback.data):
        case "Yes":
            bot.send_message(callback.message.chat.id, "Приступаем к игре! Ты ходишь первым")
            add_game(callback.message.chat.id, True)
        case "No":
            bot.send_message(callback.message.chat.id, "Поиграем в следующий раз, когда ты будешь готов")
        case _:
            bot.send_message(callback.message.chat.id, "Чта?!")
# Ввод городов
@bot.message_handler()
def print_cities(message):
    user_city = message.text; # Город пользователя
    if not(has_city(user_city)):
        bot.send_message(message.chat.id, "Такого города не существует. Попробуй ещё раз");
    elif is_reused_city(message.text, message.from_user.id):
        bot.send_message(message.chat.id, "Этот город был назван ранее. Назови другой город");
    else:
        if check_first_symbol(message.text, message.chat.id):
            bot.send_message(message.chat.id, f"Этот город не на ту букву. Назови другой город");
        else:
            add_city(message.chat.id, message.text)
            current_city = get_random_city(message.text);
            database = sql.connect(database_title)
            cursor = database.cursor()
            cursor.execute(f"INSERT INTO games (chat_id, last_symbol)  VALUES ({message.chat.id}, \"{get_last_char(current_city)}\") ON CONFLICT(chat_id) DO UPDATE SET last_symbol = excluded.last_symbol")
            database.commit()
            if current_city is None:
                bot.send_message(message.chat.id, f"Ты победил, я не могу назвать ни одного города")
            else:
                cursor.execute(f"INSERT INTO used_cities (chat_id, city_name) VALUES ({message.chat.id}, \"{current_city}\")")
                bot.send_message(message.chat.id, f"Хорошо, теперь мой город: {current_city}")
                database.commit()
            database.close()
        
bot.polling(none_stop=True) # Бот постоянно работает