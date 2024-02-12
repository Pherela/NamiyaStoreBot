import os
import random
import sqlite3
from dotenv import load_dotenv
from telebot import TeleBot, types, util


class MiracleofNamiyaStoreBot:
    def __init__(self, token, cmds):
        self.bot = TeleBot(token)
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
            self.bot.set_my_commands([types.BotCommand(cmd['cmd'], cmd[lc]) for cmd in self.cmds], language_code=lc)
            
    def help_page(self, message):
        lang_code = message.from_user.language_code
        self.cursor.execute('SELECT role FROM user_roles WHERE chat_id = ?', (message.chat.id,))
        role = self.cursor.fetchone()[0]
        for cmd in self.cmds:
            if cmd['cmd'] == 'help':
                self.bot.send_message(message.chat.id, cmd[f'{lang_code}_{role}'])


                
    def assign_role(self, message):
        if message.text == '/start':
            random.shuffle(self.roles)
            chosen_role = self.roles[0]
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
        {"cmd": "help", "en": "Guide on how to use the bot", "id": "Panduan cara menggunakan bot", "en_helper": "This is the help page. Here you can find information on how to use the bot.", "id_helper": "Ini adalah halaman bantuan. Di sini Anda dapat menemukan informasi tentang cara menggunakan bot.", "en_seeker": "This is the help page. Here you can find information on how to use the bot.", "id_seeker": "Ini adalah halaman bantuan. Di sini Anda dapat menemukan informasi tentang cara menggunakan bot."}
    ]
    bot = MiracleofNamiyaStoreBot(os.getenv('TELEGRAM_TOKEN'), cmds)
    bot.start_polling()
