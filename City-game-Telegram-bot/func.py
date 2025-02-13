import random
import sqlite3 as sql

database_title = "info.db" # Название БД
ban_symbols = ['ы', 'ъ', 'ь'] # "Запретные" буквы

# Возвращает последний символ слова в соответствии с правилами игры в города
def get_last_char_city(city_name: str) -> str:
    if (len(city_name) < 2):
        raise ValueError("len(word) < 2")
    return city_name[-1].upper() if city_name[-1] not in ban_symbols else city_name[-2].upper()

def get_last_char_batabase(chat_id: int) -> str:
    database = sql.connect(database_title)
    cursor = database.cursor()
    cursor.execute(f"SELECT last_symbol FROM games WHERE chat_id = {chat_id}")
    result = cursor.fetchone()
    database.close()
    return result[0]

# Возвращает случайный город
def get_random_city(previous_city: str) -> str:
    database = sql.connect(database_title)
    cursor = database.cursor()
    last_char = get_last_char_city(previous_city)
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
def add_or_update_game(chat_id: int, is_game_start: bool):
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
def clear_last_char(chat_id: int):
    database = sql.connect(database_title)
    cursor = database.cursor()
    cursor.execute(f"UPDATE games SET last_symbol = NULL WHERE chat_id = {chat_id}")
    database.commit()
    database.close()

def insert_or_update_last_symbol(chat_id: int, new_last_symbol: str):
    if (len(new_last_symbol) != 1):
        raise ValueError("len(new_last_symbol) != 1")
    database = sql.connect(database_title)
    cursor = database.cursor()
    cursor.execute(f"INSERT INTO games (chat_id, last_symbol)  VALUES ({chat_id}, \"{new_last_symbol}\") ON CONFLICT(chat_id) DO UPDATE SET last_symbol = excluded.last_symbol")
    database.commit()
    database.close()
# Проверяет, началась ли игра в чате с указанным индексом    
def is_game_start(chat_id: int) -> bool:
    database = sql.connect(database_title)
    cursor = database.cursor()
    cursor.execute(f"SELECT is_game_start FROM games WHERE chat_id = {chat_id}")
    result = cursor.fetchone()
    database.close()
    return result is not None and result[0]
        
# Проверяет правильность первого символа в названии города
def check_first_symbol(city_name: str, chat_id: int) -> bool:
    database = sql.connect(database_title)
    cursor = database.cursor()
    cursor.execute(f"SELECT last_symbol FROM games WHERE chat_id = {chat_id}")
    temp = cursor.fetchone()
    database.close()
    return temp is not None and temp[0] is not None and city_name[0].upper() != temp[0][0].upper()
        