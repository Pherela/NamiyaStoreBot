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
        self.bot.message_handler(commands=['help'])(self.help_page)
        

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
            
    def help_page(self, message):
        help_text = "This is the help page. Here you can find information on how to use the bot."
        self.bot.send_message(message.chat.id, help_text) 
        
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
        {"cmd": "start", "en": "Begin", "id": "Mulai", "en_helper": "Welcome! Let's guide.", "id_helper": "Selamat datang! Mari kita beri petunjuk.", "en_seeker": "Welcome! Let's seek answers.", "id_seeker": "Selamat datang! Mari kita cari petunjuk."},
        {"cmd": "help", "en": "Guide on how to use the bot", "id": "Panduan cara menggunakan bot"}
    ]
    bot = MiracleofNamiyaStoreBot(os.getenv('TELEGRAM_TOKEN'), cmds)
    bot.start_polling()
    bot = MiracleofNamiyaStoreBot(os.getenv('TELEGRAM_TOKEN'), cmds)
    bot.start_polling()
