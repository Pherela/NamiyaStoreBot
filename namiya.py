import os
import random
from telebot import TeleBot, types, util
from dotenv import load_dotenv

class MiracleofNamiyaStoreBot:
    def __init__(self, token):
        self.bot = TeleBot(token)
        self.user_roles = {}
        self.roles = ['helper', 'seeker']
        self.messages = {
            '/helper': "You have chosen the role of helper.",
            '/seeker': "You have chosen the role of seeker."
        }
        self.commands = ['/helper', '/seeker', '/start', '/random']
        self.forwarded_messages = {}

        self.bot.message_handler(commands=['start', 'random', 'helper', 'seeker'])(self.assign_role)
        self.bot.message_handler(func=lambda message: True)(self.forward_message)
        self.bot.message_handler(func=lambda message: True, content_types=['text'])(self.reply_to_seeker)
        self.bot.message_handler(commands=['rate'])(self.rate_response)
    
    def set_commands(self, cmds):
        for lc in cmds[0].keys() - {'cmd'}:
            self.bot.set_my_commands([types.BotCommand(c['cmd'], c[lc]) for c in cmds], language_code=lc)    
    def assign_role(self, message):
        if util.is_command(message.text):
            if message.text in self.commands:
                if message.text == '/start' or message.text == '/random':
                    chosen_role = random.choice(self.roles)
                    self.bot.reply_to(message, "You have been randomly assigned the role of {}.".format(chosen_role))
                else:
                    chosen_role = self.roles[self.commands.index(message.text)]
                    self.bot.reply_to(message, self.messages[message.text])
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
            
    def start_polling(self):
        self.bot.infinity_polling(long_polling_timeout=20)

if __name__ == "__main__":
    load_dotenv('./.env')
    bot_token = os.getenv('TELEGRAM_TOKEN')
    bot = MiracleofNamiyaStoreBot(bot_token)
    cmds = [
    {"cmd": "start", "en": "Begin", "id": "Mulai"},
    {"cmd": "random", "en": "Discover", "id": "Temukan"},
    {"cmd": "helper", "en": "Assist", "id": "Bantu"},
    {"cmd": "seeker", "en": "Seek", "id": "Cari"},
    {"cmd": "help", "en": "Guide on how to use the bot", "id": "Panduan cara menggunakan bot"}
    ]
    bot.set_commands(cmds)
    bot.start_polling()
