from re import L
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
    add_or_update_game(message.chat.id, False)
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Конечно", callback_data="Yes"))
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
            clear_used_cities(callback.message.chat.id)
            clear_last_char(callback.message.chat.id)
            add_or_update_game(callback.message.chat.id, True)
        case "Defeat":
            add_or_update_game(callback.message.chat.id, False)
            clear_used_cities(callback.message.chat.id)
            clear_last_char(callback.message.chat.id)
            bot.send_message(callback.message.chat.id, "Ты держался достойно")
        case "Last_char":
            bot.send_message(callback.message.chat.id, f"Последний символ: {get_last_char_batabase(callback.message.chat.id)}")
        case _:
            bot.send_message(callback.message.chat.id, "Чта?!")
# Ввод городов
@bot.message_handler()
def print_cities(message):
    user_city = message.text; # Город пользователя
    
    if not is_game_start(message.chat.id):
        bot.send_message(message.chat.id, "Игра еще не началась. Пожалуйста, нажмите \"Конечно\", чтобы начать игру.")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Какая последняя буква?", callback_data="Last_char"), types.InlineKeyboardButton("Я сдаюсь", callback_data="Defeat"))
    if not(has_city(user_city)):
        bot.send_message(message.chat.id, "Такого города не существует. Попробуй ещё раз", reply_markup=markup);
    elif is_reused_city(message.text, message.from_user.id):
        bot.send_message(message.chat.id, "Этот город был назван ранее. Назови другой город", reply_markup=markup);
    else:
        if check_first_symbol(message.text, message.chat.id):
            bot.send_message(message.chat.id, f"Этот город не на ту букву. Назови другой город", reply_markup=markup);
        else:
            add_city(message.chat.id, message.text)
            insert_or_update_last_symbol(message.chat.id, get_last_char_city(message.text))
            current_city = get_random_city(message.text);
            insert_or_update_last_symbol(message.chat.id, get_last_char_city(current_city))
            if current_city is None:
                bot.send_message(message.chat.id, f"Ты победил, я не могу назвать ни одного города", reply_markup=markup)
            else:
                insert_or_update_last_symbol(message.chat.id, get_last_char_city(current_city))
                add_city(message.chat.id, current_city)
                bot.send_message(message.chat.id, f"Хорошо, теперь мой город: {current_city}", reply_markup=markup)
        
bot.polling(none_stop=True) # Бот постоянно работает