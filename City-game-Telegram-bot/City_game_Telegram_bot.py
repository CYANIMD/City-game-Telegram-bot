import telebot
import sqlite3 as sql
from telebot import types

token = "" #Вставить свой токен

ban_symbol = ['ы', 'ъ', 'ь', 'й'] #"Запретные" буквы
bot = telebot.TeleBot(token)

#Возвращает случайный город из БД
def get_random_city(last_city: str) -> str:
    database = sql.connect("world_cities.db")
    cursor = database.cursor()
    last_char = last_city.upper()[-1] if last_city[-1] not in  ban_symbol else last_city.upper()[-2]
    cursor.execute(f"SELECT name FROM cities WHERE name LIKE \"{last_char}%\"")
    return cursor.fetchone()[0]
#Проверяет наличие города в БД
def check_city(city: str) -> bool:
    database = sql.connect("world_cities.db")
    cursor = database.cursor()
    cursor.execute(f"SELECT name FROM cities WHERE name = \"{city.capitalize()}\"" )
    result = cursor.fetchone()
    return result is None
    
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
@bot.message_handler()
#Отслеживание текста пользователя
def user_print_city(message):
    if check_city(message.text):
        bot.send_message(message.chat.id, "Такого города не существует. Попробуй ещё раз");
    else:
        bot.send_message(message.chat.id, f"Хорошо, теперь мой город: {get_random_city(message.text)}")
        

@bot.message_handler()
def uncorrect_message(message):
    bot.send_message(message.chat.id, "Твоё сообщение некорректное!")

bot.polling(none_stop=True)