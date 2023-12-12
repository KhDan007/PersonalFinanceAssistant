import telebot

# Replace 'YOUR_BOT_TOKEN' with the actual token obtained from BotFather
TOKEN = '6862651061:AAHxODX_mKefWJ1G6YSredHvc3IUyv8Mi5I'
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, message.text)


# Start the bot
print("Bot started successfully.")
bot.polling()
