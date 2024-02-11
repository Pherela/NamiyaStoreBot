import os
import telebot
import random
import csv
from telebot import util
from dotenv import load_dotenv

class MiracleofNamiyaStoreBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.user_roles = {}
        self.roles = ['helper', 'seeker']
        self.messages = {
            '/start': "Welcome! You have been randomly assigned the role of {}.",
            '/random': "You have been randomly assigned the role of {}.",
            '/helper': "You have chosen the role of helper.",
            '/seeker': "You have chosen the role of seeker."
        }
        self.commands = {command: role for command, role in zip(['/helper', '/seeker'], self.roles + [random.choice(self.roles) for _ in range(2)])}
        self.forwarded_messages = {}

        self.bot.message_handler(commands=['start', 'random', 'helper', 'seeker'])(self.assign_role)
        self.bot.message_handler(func=lambda message: True)(self.forward_message)
        self.bot.message_handler(func=lambda message: True, content_types=['text'])(self.reply_to_seeker)
        self.bot.message_handler(commands=['rate'])(self.rate_response)

        # Create the file if it does not exist
        if not os.path.exists('ratings.csv'):
            with open('ratings.csv', 'w') as f:
                writer = csv.writer(f)
                writer.writerow(['chat_id', 'rating'])

    def assign_role(self, message):
        if util.is_command(message.text):
            if message.text in self.commands:
                chosen_role = self.commands[message.text]
                self.bot.reply_to(message, self.messages[message.text].format(chosen_role))
                self.user_roles[message.chat.id] = chosen_role

    def forward_message(self, message):
        if self.user_roles.get(message.chat.id) == 'seeker':
            for user_id, role in self.user_roles.items():
                if role == 'helper':
                    forwarded_message = self.bot.forward_message(user_id, message.chat.id, message.message_id)
                    self.forwarded_messages[forwarded_message.message_id] = message.chat.id  # Save the original chat id

    def reply_to_seeker(self, message):
        if message.reply_to_message and message.reply_to_message.message_id in self.forwarded_messages:
            original_chat_id = self.forwarded_messages[message.reply_to_message.message_id]
            self.bot.send_message(original_chat_id, message.text)

    def rate_response(self, message):
        if message.text.startswith('/rate') and self.user_roles.get(message.chat.id) == 'seeker':
            _, rating = message.text.split()
            with open('ratings.csv', 'a') as f:
                writer = csv.writer(f)
                writer.writerow([message.chat.id, rating])
            self.bot.reply_to(message, "Thank you for your feedback!")
        else:
            self.bot.reply_to(message, "Only seekers can rate responses.")

    def start_polling(self):
        self.bot.polling(none_stop=True, interval=0, timeout=20)

if __name__ == "__main__":
    load_dotenv('./.env')
    bot_token = os.getenv('TELEGRAM_TOKEN')
    bot = MiracleofNamiyaStoreBot(bot_token)
    bot.start_polling()
