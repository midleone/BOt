import psycopg2
from psycopg2 import sql

# Параметры подключения к базе данных
DB_NAME = 'volonteers'
DB_USER = 'postgres'
DB_PASSWORD = '142321'
DB_HOST = 'localhost'
DB_PORT = '5432'

# Подключение к базе данных
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

# Чтение текста из файла events.txt
with open('events.txt', 'r', encoding='utf-8') as file:
    events_text = file.read()

# Разбиваем текст на строки
events_lines = events_text.split('\n')

# Перебираем каждую строку события
for event_line in events_lines:
    # Проверяем, что в строке есть значения для разбиения
    if ',' not in event_line:
        continue

    # Парсим колонки из строки
    values = event_line.split(',')

    # Проверяем, что есть как минимум три значения
    if len(values) < 3:
        print(f"Skipping line: {event_line}. Not enough values.")
        continue

    city, interests, volunteer_experience = values[:3]

    # Подготовка SQL-запроса
    query = sql.SQL(
        "SELECT last_name FROM volonteers WHERE city = %s AND interests = %s AND volunteer_experience = %s;")
    data = (city.strip(), interests.strip(), volunteer_experience.strip())

    # Выполнение запроса
    cursor.execute(query, data)

    # Получение результатов
    result = cursor.fetchone()

    # Вывод last_name при совпадении
    if result:
        print(f"Match found! Last Name: {result[0]}")

# Закрытие соединения с базой данных
cursor.close()
conn.close()
