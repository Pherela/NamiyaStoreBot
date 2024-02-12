import os
import random
import sqlite3
from dotenv import load_dotenv
from telebot import TeleBot, types


class MiracleofNamiyaStoreBot:
    def __init__(self, token):
        self.bot = TeleBot(token)
        self.user_roles = {}
        self.roles = ['helper', 'seeker']
        self.setup_database()
        self.forwarded_messages = {}

        self.bot.message_handler(commands=['start'])(self.assign_role)
        self.bot.message_handler(func=lambda message: True)(self.forward_message)
        self.bot.message_handler(func=lambda message: True, content_types=['text'])(self.reply_to_seeker)

    def setup_database(self):
        self.conn = sqlite3.connect('user_roles.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_roles (
                chat_id INTEGER PRIMARY KEY,
                role TEXT
            )
        ''')
        self.conn.commit()
        
    def set_commands(self, cmds):
        for lc in cmds[0].keys() - {'cmd'}:
            self.bot.set_my_commands([types.BotCommand(c['cmd'], c[lc]) for c in cmds], language_code=lc)    
    def assign_role(self, message):
        if message.text == '/start':
            chosen_role = random.choice(self.roles)
            self.cursor.execute('REPLACE INTO user_roles VALUES (?, ?)', (message.chat.id, chosen_role))
            self.conn.commit()
            self.bot.send_message(message.chat.id, f"You have been randomly assigned the role of {chosen_role}.")

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
    bot = MiracleofNamiyaStoreBot(os.getenv('TELEGRAM_TOKEN'))
    cmds = [
    {"cmd": "start", "en": "Begin", "id": "Mulai"},
    {"cmd": "help", "en": "Guide on how to use the bot", "id": "Panduan cara menggunakan bot"}
    ]
    bot.set_commands(cmds)
    bot.start_polling()
