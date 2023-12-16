import telebot
from telebot import types
import psycopg2

TOKEN = '6954905060:AAFGmwHLcjBWnQlp4gH7mr5j0vxgfSpZ7fQ'
bot = telebot.TeleBot(TOKEN)

# Параметры подключения к PostgreSQL
DB_NAME = 'volonteers'
DB_USER = 'postgres'
DB_PASSWORD = '142321'
DB_HOST = 'localhost'
DB_PORT = '5432'

# Словарь для хранения данных пользователей
users = {}


# Функция для подключения к базе данных
def connect_to_db():
    return psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD, host=DB_HOST, port=DB_PORT)

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id

    if user_id in users:
        bot.send_message(user_id, f"Hello, {users[user_id]['first_name']}!")
    else:
        bot.send_message(user_id, "Добро пожаловать! Пожалуйста, зарегистрируйтесь.")

        # Запрос данных для регистрации
        bot.send_message(user_id, "Введите ваше Имя:")
        bot.register_next_step_handler(message, process_first_name)

def process_first_name(message):
    user_id = message.from_user.id
    users[user_id] = {'first_name': message.text}

    # Запрос остальных данных
    bot.send_message(user_id, "Введите вашу Фамилию:")
    bot.register_next_step_handler(message, process_last_name)

def process_last_name(message):
    user_id = message.from_user.id
    users[user_id]['last_name'] = message.text

    bot.send_message(user_id, "Введите ваш Номер телефона:")
    bot.register_next_step_handler(message, process_phone_number)

def process_phone_number(message):
    user_id = message.from_user.id
    users[user_id]['phone_number'] = message.text

    bot.send_message(user_id, "Введите вашу Почту:")
    bot.register_next_step_handler(message, process_email)

def process_email(message):
    user_id = message.from_user.id
    users[user_id]['email'] = message.text

    bot.send_message(user_id, "Введите ваш Город проживания:")
    bot.register_next_step_handler(message, process_city)

def process_city(message):
    user_id = message.from_user.id
    users[user_id]['city'] = message.text

    bot.send_message(user_id, "Введите ваши Интересы:")
    bot.register_next_step_handler(message, process_interests)

def process_interests(message):
    user_id = message.from_user.id
    users[user_id]['interests'] = message.text

    bot.send_message(user_id, "Введите ваш Предыдущий опыт в волонтерстве:")
    bot.register_next_step_handler(message, process_volunteer_experience)

@bot.message_handler(commands=['delete_account'])
def handle_delete_account(message):
    user_id = message.from_user.id

    if user_exists(user_id):
        delete_user(user_id)
        bot.send_message(user_id, "Ваш аккаунт успешно удален.")
    else:
        bot.send_message(user_id, "Вы не зарегистрированы.")

def process_volunteer_experience(message):
    user_id = message.from_user.id
    users[user_id]['volunteer_experience'] = message.text

    # Сохранение данных в базе данных
    save_data_to_db(user_id)

    # Приветствие после регистрации
    bot.send_message(user_id, f"Регистрация завершена. Привет, {users[user_id]['first_name']}!")

def save_data_to_db(user_id):
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        # Создание таблицы, если она не существует
        create_table_query = """
        CREATE TABLE IF NOT EXISTS user_data (
            user_id BIGINT PRIMARY KEY,
            first_name VARCHAR(255),
            last_name VARCHAR(255),
            phone_number VARCHAR(20),
            email VARCHAR(255),
            city VARCHAR(255),
            interests TEXT,
            volunteer_experience TEXT
        );
        """
        cursor.execute(create_table_query)

        # Вставка данных
        insert_query = """
        INSERT INTO user_data (
            user_id, first_name, last_name, phone_number, email, city, interests, volunteer_experience
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        user_data = (
            user_id,
            users[user_id]['first_name'],
            users[user_id]['last_name'],
            users[user_id]['phone_number'],
            users[user_id]['email'],
            users[user_id]['city'],
            users[user_id]['interests'],
            users[user_id]['volunteer_experience']
        )
        cursor.execute(insert_query, user_data)

        connection.commit()

    except Exception as e:
        print(f"Error saving data to the database: {e}")

def delete_user(user_id):
    try:
        connection = connect_to_db()
        cursor = connection.cursor()

        delete_query = "DELETE FROM user_data WHERE user_id = %s"
        cursor.execute(delete_query, (user_id,))

        connection.commit()

    except Exception as e:
        print(f"Error deleting user: {e}")


    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    bot.polling(none_stop=True)







