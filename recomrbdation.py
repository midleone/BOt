import psycopg2
from psycopg2 import sql

DB_NAME = 'volonteers'
DB_USER = 'postgres'
DB_PASSWORD = '142321'
DB_HOST = 'localhost'
DB_PORT = '5432'

conn = psycopg2.connect(
    dbname=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT
)
cursor = conn.cursor()

with open('events.txt', 'r', encoding='utf-8') as file:
    events_text = file.read()

events_lines = events_text.split('\n')

for event_line in events_lines:
    if ',' not in event_line:
        continue

    values = event_line.split(',')

    if len(values) < 3:
        print(f"Skipping line: {event_line}. Not enough values.")
        continue

    city, interests, volunteer_experience = values[:3]

    query = sql.SQL(
        "SELECT last_name FROM volonteers WHERE city = %s AND interests = %s AND volunteer_experience = %s;")
    data = (city.strip(), interests.strip(), volunteer_experience.strip())

    cursor.execute(query, data)

    result = cursor.fetchone()

    if result:
        print(f"Match found! Last Name: {result[0]}")

# Закрытие соединения с базой данных
cursor.close()
conn.close()
