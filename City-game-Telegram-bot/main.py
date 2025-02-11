from func import *
import telebot
from telebot import types
import sqlite3 as sql
import random

token = "" #Вставить свой токен
bot = telebot.TeleBot(token) #Инициализация бота

#Запуск бота
@bot.message_handler(commands=["start", "main"])
def main(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Да!", callback_data="Yes"),types.InlineKeyboardButton("Нет...", callback_data="No"))
    bot.send_message(message.chat.id, "Привет! Я телеграм бот, с которым можно поиграть в города. Вот правила игры:"+
                     "\n(1). Один из игроков называет случайный город;"+
                     "\n(2). Каждый игрок по очереди называет город, который начинается на последнюю букву города (за некоторым исключением), названного предыдущим игроком;"+
                     "\n(3). Нельзя повторять города, которые уже были названы в ходе игры;"+
                     "\n(4). Города должны быть настоящими;"+
                     "\n(5). Если город, названный игроком, заканчивается на букву \"ы\", \"ь\", \"ъ\" или \"й\", то следующий игрок должен назвать город, начинающийся с предпоследней буквы города, названного предыдущим игроком\n" +
                     "Ты готов к игре?", reply_markup=markup)

#Отслеживание нажатия на кнопку
@bot.callback_query_handler(func=lambda call: True)
def press_button(callback):
    match(callback.data):
        case "Yes":
            bot.send_message(callback.message.chat.id, "Приступаем к игре! Ты ходишь первым")
        case "No":
            bot.send_message(callback.message.chat.id, "Поиграем в следующий раз, когда ты будешь готов")
        case _:
            bot.send_message(callback.message.chat.id, "Чта?!")
#Пользователь вводит город
@bot.message_handler()
def user_print_city(message):
    if has_city(message.text):
        bot.send_message(message.chat.id, "Такого города не существует. Попробуй ещё раз");
    elif is_reused_city(message.text, message.from_user.id):
        bot.send_message(message.chat.id, "Этот город уже был! Назови другой город");
    else:
        database = sql.connect(database_title)
        cursor = database.cursor()
        cursor.execute(f"SELECT symbol FROM last_symbols WHERE user_id = {message.from_user.id}")
        temp = cursor.fetchone()
        if temp is not None and message.text[0].upper() != temp[0].upper():
            bot.send_message(message.chat.id, f"Этот город не на ту букву. Назови другой город на букву {temp[0].upper()}");
        else:
            cursor.execute("INSERT INTO chats (chat_id, city_name) VALUES (?, ?)", (message.chat.id, message.text))
            database.commit()
            current_city = get_random_city(message.text);
            cursor.execute("INSERT INTO last_symbols (user_id, symbol)  VALUES (?, ?)  ON CONFLICT(user_id) DO UPDATE SET symbol = excluded.symbol", (message.from_user.id, get_last_char(current_city)))
            database.commit()
            if current_city is None:
                bot.send_message(message.chat.id, f"Ты победил, я не могу назвать ни одного города")
            else:
                cursor.execute("INSERT INTO chats (chat_id, city_name) VALUES (?, ?)", (message.chat.id, current_city))
                bot.send_message(message.chat.id, f"Хорошо, теперь мой город: {current_city}")
                database.commit()
            database.close()
        
bot.polling(none_stop=True)