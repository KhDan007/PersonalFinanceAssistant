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


# Function to handle the /setbudget command
@bot.message_handler(commands=['setbudget'])
def set_budget(message):
    conn, cursor = None, None  # Initialize variables
    try:
        user_id = message.from_user.id
        # Extract parameters from the command
        _, category, goal_amount = message.text.split(' ', 2)
        goal_amount = float(goal_amount)

        # Create a new database connection and cursor
        conn, cursor = get_database_connection()

        # Check if the category already exists in the budgets table
        cursor.execute("SELECT * FROM budgets WHERE user_id = ? AND category = ?", (user_id, category))
        result = cursor.fetchone()

        if result:
            # Update the existing budget
            cursor.execute("UPDATE budgets SET goal_amount = ? WHERE user_id = ? AND category = ?",
                           (goal_amount, user_id, category))
            reply_text = f"Budget for '{category}' updated successfully! New goal: ${goal_amount:.2f}"
        else:
            # Insert a new budget
            cursor.execute("INSERT INTO budgets (user_id, category, goal_amount, current_amount) VALUES (?, ?, ?, 0.0)",
                           (user_id, category, goal_amount))
            reply_text = f"Budget for '{category}' set successfully with a goal of ${goal_amount:.2f}!"

        conn.commit()
        bot.reply_to(message, reply_text)

    except ValueError:
        bot.reply_to(message, "Please provide a valid goal amount. Example: /setbudget groceries 200.0")

    except IndexError:
        bot.reply_to(message, "Please provide all required parameters. Example: /setbudget groceries 200.0")

    except sqlite3.Error as e:
        bot.reply_to(message, f"An error occurred: {e}")

    finally:
        # Close the database connection
        close_database_connection(conn, cursor)


# Function to handle the /addexpense command
@bot.message_handler(commands=['addexpense'])
def add_expense(message):
    conn, cursor = None, None  # Initialize variables
    try:
        user_id = message.from_user.id
        # Extract parameters from the command
        _, category, amount, date = message.text.split(' ', 3)
        amount = float(amount)
        date = date.strip()

        # Create a new database connection and cursor
        conn, cursor = get_database_connection()

        # Check if the category exists in the budgets table
        cursor.execute("SELECT * FROM budgets WHERE user_id = ? AND category = ?", (user_id, category))
        result = cursor.fetchone()

        if result:
            _, _, _, goal_amount, current_amount = result

            # Update the current amount with the new expense
            current_amount += amount

            # Update the budgets table
            cursor.execute("UPDATE budgets SET current_amount = ? WHERE user_id = ? AND category = ?",
                           (current_amount, user_id, category))
            conn.commit()

            reply_text = f"Expense of ${amount:.2f} added to '{category}' successfully!"
        else:
            reply_text = f"You don't have a budget set for '{category}'. Please set a budget first."

        bot.reply_to(message, reply_text)

    except ValueError:
        bot.reply_to(message, "Please provide a valid amount. Example: /addexpense groceries 50.0 2023-12-31")

    except IndexError:
        bot.reply_to(message, "Please provide all required parameters. Example: /addexpense groceries 50.0 2023-12-31")

    except sqlite3.Error as e:
        bot.reply_to(message, f"An error occurred: {e}")

    finally:
        # Close the database connection
        close_database_connection(conn, cursor)


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
