import telebot
import psycopg2
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler, CallbackContext

class VolunteerBot:
    def __init__(self, token, db_name, db_user, db_password, db_host, db_port):
        self.token = token
        self.bot = telebot.TeleBot(token)
        self.db_name = db_name
        self.db_user = db_user
        self.db_password = db_password
        self.db_host = db_host
        self.db_port = db_port
        self.users = {}

        # Initialize the database
        self.init_db()

        # Register handlers
        self.register_handlers()

    def init_db(self):
        try:
            connection = self.connect_to_db()
            cursor = connection.cursor()

            # Create user_data table if not exists
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
            connection.commit()

        except Exception as e:
            print(f"Error initializing the database: {e}")

        finally:
            if connection:
                connection.close()

    def connect_to_db(self):
        return psycopg2.connect(dbname=self.db_name, user=self.db_user, password=self.db_password,
                                host=self.db_host, port=self.db_port)

    def register_handlers(self):
        updater = Updater(self.token, use_context=True)
        dp = updater.dispatcher

        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.handle_start)],
            states={
                'ASK_NAME': [MessageHandler(Filters.text & ~Filters.command, self.process_name)],
                'ASK_LAST_NAME': [MessageHandler(Filters.text & ~Filters.command, self.process_last_name)],
                'ASK_PHONE_NUMBER': [MessageHandler(Filters.text & ~Filters.command, self.process_phone_number)],
                'ASK_EMAIL': [MessageHandler(Filters.text & ~Filters.command, self.process_email)],
                'ASK_CITY': [MessageHandler(Filters.text & ~Filters.command, self.process_city)],
                'ASK_INTERESTS': [MessageHandler(Filters.text & ~Filters.command, self.process_interests)],
                'ASK_EXPERIENCE': [MessageHandler(Filters.text & ~Filters.command, self.process_volunteer_experience)],
            },
            fallbacks=[]
        )

        dp.add_handler(conv_handler)
        dp.add_handler(CommandHandler('delete_account', self.handle_delete_account))
        dp.add_handler(CommandHandler('register_event', self.handle_register_event))

        updater.start_polling()
        updater.idle()

    def handle_start(self, update, context):
        user_id = update.message.from_user.id

        if user_id in self.users:
            self.bot.send_message(user_id, f"Hello, {self.users[user_id]['first_name']}!")
        else:
            self.bot.send_message(user_id, "Welcome! Please register.")
            self.bot.send_message(user_id, "Enter your Name:")
            return 'ASK_NAME'

    def process_name(self, update, context):
        user_id = update.message.from_user.id
        self.users[user_id] = {'first_name': update.message.text}

        self.bot.send_message(user_id, "Enter your Last Name:")
        return 'ASK_LAST_NAME'

    def process_last_name(self, update, context):
        user_id = update.message.from_user.id
        self.users[user_id]['last_name'] = update.message.text

        self.bot.send_message(user_id, "Enter your Phone Number:")
        return 'ASK_PHONE_NUMBER'

    def process_phone_number(self, update, context):
        user_id = update.message.from_user.id
        self.users[user_id]['phone_number'] = update.message.text

        self.bot.send_message(user_id, "Enter your Email:")
        return 'ASK_EMAIL'

    def process_email(self, update, context):
        user_id = update.message.from_user.id
        self.users[user_id]['email'] = update.message.text

        self.bot.send_message(user_id, "Enter your City:")
        return 'ASK_CITY'

    def process_city(self, update, context):
        user_id = update.message.from_user.id
        self.users[user_id]['city'] = update.message.text

        self.bot.send_message(user_id, "Enter your Interests:")
        return 'ASK_INTERESTS'

    def process_interests(self, update, context):
        user_id = update.message.from_user.id
        self.users[user_id]['interests'] = update.message.text

        self.bot.send_message(user_id, "Enter your Volunteer Experience:")
        return 'ASK_EXPERIENCE'

    def process_volunteer_experience(self, update, context):
        user_id = update.message.from_user.id
        self.users[user_id]['volunteer_experience'] = update.message.text

        # Save data to the database
        self.save_data_to_db(user_id)

        # Greet after registration
        self.bot.send_message(user_id, f"Registration completed. Hello, {self.users[user_id]['first_name']} to registration for event put /register_event and to delete account put /delete_account!")

    def handle_delete_account(self, update, context):
        user_id = update.message.from_user.id

        if self.user_exists(user_id):
            self.delete_user(user_id)
            self.bot.send_message(user_id, "Your account has been successfully deleted.")
        else:
            self.bot.send_message(user_id, "You are not registered.")

    def handle_register_event(self, update, context):
        user_id = update.message.from_user.id

        if self.user_exists(user_id):
            self.bot.send_message(user_id, "To register for an event, send the post number. Example: id123")
            return 'EVENT_REGISTRATION'
        else:
            self.bot.send_message(user_id, "You are not registered. Please register using /start.")

    def process_event_registration(self, update, context):
        user_id = update.message.from_user.id
        post_id = update.message.text

        if self.user_exists(user_id):
            self.save_event_registration_to_db(user_id, post_id)
            self.bot.send_message(user_id, f"You have successfully registered for the event with post number {post_id}.")
        else:
            self.bot.send_message(user_id, "You are not registered. Please register using /start.")

    def save_event_registration_to_db(self, user_id, post_id):
        try:
            connection = self.connect_to_db()
            cursor = connection.cursor()

            # Create applications table if not exists
            create_applications_table_query = """
            CREATE TABLE IF NOT EXISTS applications (
                id SERIAL PRIMARY KEY,
                user_name VARCHAR(255),
                post_id VARCHAR(255)
            );
            """
            cursor.execute(create_applications_table_query)

            # Insert data
            insert_query = "INSERT INTO applications (user_name, post_id) VALUES (%s, %s)"
            user_name = f"{self.users[user_id]['first_name']} {self.users[user_id]['last_name']}"
            cursor.execute(insert_query, (user_name, post_id))

            connection.commit()

        except Exception as e:
            print(f"Error saving event registration data to the database: {e}")

        finally:
            if connection:
                connection.close()

    def save_data_to_db(self, user_id):
        try:
            connection = self.connect_to_db()
            cursor = connection.cursor()

            # Insert data into user_data table
            insert_query = """
            INSERT INTO user_data (
                user_id, first_name, last_name, phone_number, email, city, interests, volunteer_experience
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            user_data = (
                user_id,
                self.users[user_id]['first_name'],
                self.users[user_id]['last_name'],
                self.users[user_id]['phone_number'],
                self.users[user_id]['email'],
                self.users[user_id]['city'],
                self.users[user_id]['interests'],
                self.users[user_id]['volunteer_experience']
            )
            cursor.execute(insert_query, user_data)

            connection.commit()

        except Exception as e:
            print(f"Error saving data to the database: {e}")

        finally:
            if connection:
                connection.close()

    def delete_user(self, user_id):
        try:
            connection = self.connect_to_db()
            cursor = connection.cursor()

            # Delete user from user_data table
            delete_query = "DELETE FROM user_data WHERE user_id = %s"
            cursor.execute(delete_query, (user_id,))

            connection.commit()

        except Exception as e:
            print(f"Error deleting user: {e}")

        finally:
            if connection:
                connection.close()

    def user_exists(self, user_id):
        try:
            connection = self.connect_to_db()
            cursor = connection.cursor()

            # Check if the user exists in user_data table
            check_user_query = "SELECT * FROM user_data WHERE user_id = %s"
            cursor.execute(check_user_query, (user_id,))
            return cursor.fetchone() is not None

        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False

        finally:
            if connection:
                connection.close()

if __name__ == "__main__":
    TOKEN = '6954905060:AAFGmwHLcjBWnQlp4gH7mr5j0vxgfSpZ7fQ'
    DB_NAME = 'volonteers'
    DB_USER = 'postgres'
    DB_PASSWORD = '142321'
    DB_HOST = 'localhost'
    DB_PORT = '5432'

    volunteer_bot = VolunteerBot(TOKEN, DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT)
