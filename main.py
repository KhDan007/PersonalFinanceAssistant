import telebot
import sqlite3
from telebot import types

# Replace 'YOUR_BOT_TOKEN' with the actual token obtained from BotFather
TOKEN = '6862651061:AAHxODX_mKefWJ1G6YSredHvc3IUyv8Mi5I'
bot = telebot.TeleBot(TOKEN)

# Function to create a new database connection and cursor
def get_database_connection():
    conn = sqlite3.connect('finance_bot.db')
    cursor = conn.cursor()
    return conn, cursor

# Function to close the database connection
def close_database_connection(conn, cursor):
    try:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    except sqlite3.Error as close_error:
        print(f"Error closing SQLite connection: {close_error}")

# Function to handle the /checkbudget command
@bot.message_handler(commands=['checkbudget'])
def check_budget(message):
    conn, cursor = None, None  # Initialize variables
    try:
        user_id = message.from_user.id
        category = message.text.split(' ', 1)[1].strip()  # Extract category from the command

        # Create a new database connection and cursor
        conn, cursor = get_database_connection()

        # Retrieve budget information from the database
        cursor.execute("SELECT * FROM budgets WHERE user_id = ? AND category = ?", (user_id, category))
        result = cursor.fetchone()

        if result:
            _, _, category, goal_amount, current_amount = result
            reply_text = f"Your budget for '{category}' is: ${goal_amount:.2f}\nCurrent amount spent: ${current_amount:.2f}"
        else:
            reply_text = f"You don't have a budget set for '{category}' yet."

        bot.reply_to(message, reply_text)

    except IndexError:
        bot.reply_to(message, "Please specify a category. Example: /checkbudget groceries")

    except sqlite3.Error as e:
        bot.reply_to(message, f"An error occurred: {e}")

    finally:
        # Close the database connection
        close_database_connection(conn, cursor)

# Start the bot
print('the bot is running')
bot.polling()
