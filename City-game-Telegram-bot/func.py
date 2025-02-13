import random
import sqlite3 as sql

database_title = "info.db"
ban_symbols = ['ы', 'ъ', 'ь'] # "Запретные" буквы

# Возвращает последний символ слова в соответствии с правилами игры в города
def get_last_char(word: str) -> str:
    if (len(word) < 2):
        raise ValueError("len(word) < 2")
    return word[-1].upper() if word[-1] not in ban_symbols else word[-2].upper()
# Возвращает случайный город
def get_random_city(previous_city: str) -> str:
    database = sql.connect(database_title)
    cursor = database.cursor()
    last_char = get_last_char(previous_city)
    cursor.execute(f"SELECT name FROM world_cities WHERE name LIKE \"{last_char}%\"")
    results = cursor.fetchall()
    database.close()
    return None if results is None else random.choice(results)[0]
# Проверяет, был ли назван ранее указанный город
def is_reused_city(city_name: str, chat_id: int) -> bool:
    database = sql.connect(database_title)
    cursor = database.cursor()
    cursor.execute(f"SELECT * FROM used_cities WHERE city_name = \"{city_name}\" AND chat_id = \"{chat_id}\"")
    result = cursor.fetchone()
    database.close()
    return result is not None
# Проверяет наличие города в БД
def has_city(city_name: str) -> bool:
    database = sql.connect(database_title)
    cursor = database.cursor()
    cursor.execute(f"SELECT * FROM world_cities WHERE name = \"{city_name.capitalize()}\"" )
    result = cursor.fetchone()
    database.close()
    return result is not None
# Добавляет или обновляет игру с указанием статуса
def add_game(chat_id: int, is_game_start: bool):
    database = sql.connect(database_title)
    cursor = database.cursor()
    cursor.execute(f"INSERT INTO games (chat_id, is_game_start) VALUES ({chat_id}, {is_game_start})" + 
                   f"ON CONFLICT (chat_id) DO UPDATE SET is_game_start = {is_game_start}")
    database.commit()
    database.close()
# Добавляет названный город в БД
def add_city(chat_id: int, city_name: str):
    database = sql.connect(database_title)
    cursor = database.cursor()
    cursor.execute(f"INSERT INTO used_cities (chat_id, city_name) VALUES ({chat_id}, \"{city_name}\")")
    database.commit()
    database.close()
# Очещает использованные в указанном чате города
def clear_used_cities(chat_id: int):
    database = sql.connect(database_title)
    cursor = database.cursor()
    cursor.execute(f"DELETE FROM used_cities WHERE chat_id = {chat_id}")
    database.commit()
    database.close()
# Проверяет правильность первого символа в названии города
def check_first_symbol(city_name: str, chat_id: int) -> bool:
    database = sql.connect(database_title)
    cursor = database.cursor()
    cursor.execute(f"SELECT last_symbol FROM games WHERE chat_id = {chat_id}")
    temp = cursor.fetchone()
    database.close()
    return temp is not None and temp[0] is not None and city_name[0].upper() != temp[0][0].upper()
        