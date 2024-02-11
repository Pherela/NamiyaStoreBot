import os
import telebot
import random
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
        self.commands = {command: role for command, role in zip(['/helper', '/seeker', '/start', '/random'], self.roles + [None, None])}
        self.bot.message_handler(commands=['start', 'random', 'helper', 'seeker'])(self.assign_role)
        self.bot.message_handler(func=lambda message: True)(self.forward_message)

    def assign_role(self, message):
        chosen_role = self.commands[message.text] if message.text in ['/helper', '/seeker'] else random.choice(self.roles)
        self.user_roles[message.chat.id] = chosen_role  # Save the user's role
        self.bot.reply_to(message, self.messages[message.text].format(chosen_role))

    def forward_message(self, message):
        if self.user_roles.get(message.chat.id) == 'seeker':
            for user_id, role in self.user_roles.items():
                if role == 'helper':
                    self.bot.forward_message(user_id, message.chat.id, message.message_id)

    def start_polling(self):
        self.bot.polling()

if __name__ == "__main__":
    load_dotenv('./.env')
    bot_token = os.getenv('TELEGRAM_TOKEN')
    MiracleofNamiyaStoreBot(bot_token).start_polling()
