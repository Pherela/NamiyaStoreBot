import os
import random
import sqlite3
from dotenv import load_dotenv
from telebot import TeleBot, types, util


class MiracleofNamiyaStoreBot:
    def __init__(self, token, cmds):
        self.bot = TeleBot(token)
        self.user_roles = {}
        self.roles = ['helper', 'seeker']
        self.setup_database()
        self.forwarded_messages = {}
        self.cmds = cmds
        self.bot.message_handler(commands=['start'])(self.assign_role)

    def setup_database(self):
        self.conn = sqlite3.connect('user_roles.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_roles (
                chat_id INTEGER PRIMARY_KEY,
                role TEXT
            )
        ''')
        
    def set_commands(self):
        for lc in self.cmds[0].keys() - {'cmd'}:
            self.bot.set_my_commands([types.BotCommand(c['cmd'], c[lc]) for c in self.cmds], language_code=lc)
            
    def assign_role(self, message):
        if message.text == '/start':
            chosen_role = random.choice(self.roles)
            self.cursor.execute('REPLACE INTO user_roles VALUES (?, ?)', (message.chat.id, chosen_role))
            self.conn.commit()
            for cmd in self.cmds:
                if cmd['cmd'] == 'start':
                    if message.from_user.language_code == 'id':
                        self.bot.send_message(message.chat.id, cmd[f'id_{chosen_role}'])
                    else:
                        self.bot.send_message(message.chat.id, cmd[f'en_{chosen_role}'])
                        
    def start_polling(self):
        self.bot.infinity_polling(long_polling_timeout=20)

if __name__ == "__main__":
    load_dotenv('./.env')
    cmds = [
    {"cmd": "start", "en": "Begin", "id": "Mulai", "en_helper": "Welcome to Namiya's Store! Let's provide guidance to those in need.", "id_helper": "Selamat datang di Toko Namiya! Mari kita berikan petunjuk kepada mereka yang membutuhkan.", "en_seeker": "Welcome to Namiya's Store! Let's seek answers to your questions.", "id_seeker": "Selamat datang di Toko Namiya! Mari kita cari petunjuk untuk pertanyaan yang Anda miliki."},
    {"cmd": "help", "en": "Guide on how to use the bot", "id": "Panduan cara menggunakan bot"}
    ]
    bot = MiracleofNamiyaStoreBot(os.getenv('TELEGRAM_TOKEN'), cmds)
    bot.start_polling()
