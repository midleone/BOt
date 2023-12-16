import psycopg2
import requests
from bs4 import BeautifulSoup

from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT
from sqlalchemy import create_engine, select, func, String
from sqlalchemy import create_engine, Column, Integer, MetaData, Table, select, func

def get_msg(channel: str, post: int) -> bool:
    result = requests.get(
        url=f'https://t.me/{channel}/{post}?embed=1&mode=tme'
    )

    if (result.status_code != 200):
        return False
    soup = BeautifulSoup(result.text, 'lxml')

    try:
        msg_text = soup.select_one(".tgme_widget_message_text").get_text(strip=True)

        print(msg_text)
    except Exception as e:
        return False
    return True

# def connect_to_db():
#     return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

db_url = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

# Создаем подключение
engine = create_engine(db_url)

# Создаем метаданные
metadata = MetaData()

# Определяем таблицу
posts = Table('posts', metadata,
              Column('id', Integer, primary_key=True),
              Column('channel_name', String(255)),
              Column('post_id', Integer),
              Column('text', String(4096))
              )

# Создаем соединение с базой данных
conn = engine.connect()

posts = Table('posts', metadata, autoload_with=engine)

sql_query = select([func.max(posts.c.post_id).label('max_post_id')])
result = conn.execute(sql_query).scalar()
# max_post_id = cursor.execute("SELECT MAX(post_id) AS max_value FROM posts").scalar()

conn.close()

print(f"Максимальное значение post_id: {max_post_id}")

if __name__ == '__main__':

    get_msg("volonterrcom", 4)
