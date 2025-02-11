import random
import sqlite3 as sql

database_title = "info.db"
ban_symbol = ['ы', 'ъ', 'ь'] #"Запретные" буквы

#Возвращает последний символ слова в соответствии с правилами игры в города
def get_last_char(word: str) -> str:
    return word[-1].upper() if word[-1] not in ban_symbol else word[-2].upper()
#Возвращает случайный город из БД
def get_random_city(previous_city: str) -> str:
    database = sql.connect(database_title)
    cursor = database.cursor()
    last_char = get_last_char(previous_city)
    cursor.execute(f"SELECT name FROM cities WHERE name LIKE \"{last_char}%\"")
    results = cursor.fetchall()
    database.close()
    return None if results is None else random.choice(results)[0]
#Проверяет, был ли назван указанный город ранее
def is_reused_city(city_name: str, chat_id: int) -> bool:
    database = sql.connect(database_title)
    cursor = database.cursor()
    cursor.execute(f"SELECT * FROM chats WHERE city_name = \"{city_name}\" AND chat_id = \"{chat_id}\"")
    result = cursor.fetchone()
    database.close()
    return result is not None
#Проверяет наличие города в БД
def has_city(city_name: str) -> bool:
    database = sql.connect(database_title)
    cursor = database.cursor()
    cursor.execute(f"SELECT city_id, name FROM cities WHERE name = \"{city_name.capitalize()}\"" )
    result = cursor.fetchone()
    database.close()
    return result is None