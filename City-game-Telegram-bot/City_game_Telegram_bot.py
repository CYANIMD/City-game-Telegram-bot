import telebot
from telebot import types

token = "" #Вставить свой токен

bot = telebot.TeleBot(token)

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
def uncorrect_message(message):
    bot.send_message(message.chat.id, "Твоё сообщение некорректное!")

bot.polling(none_stop=True)