import os
import random
import sqlite3
from dotenv import load_dotenv
from telebot import TeleBot, types

class MiracleofNamiyaStoreBot:
    def __init__(self, token, cmds):
        self.bot = TeleBot(token)
        self.roles = ['helper', 'seeker']
        self.db = self.setup_database()
        self.cmds = cmds
        self.set_handlers()

    def setup_database(self):
        conn = sqlite3.connect('user_roles.db', check_same_thread=False)
        cursor = conn.cursor()
        cursor.execute('CREATE TABLE IF NOT EXISTS user_roles (chat_id INTEGER PRIMARY KEY, role TEXT)')
        return conn, cursor

    def set_handlers(self):
        self.bot.message_handler(commands=['start'])(self.assign_role)
        self.bot.message_handler(commands=['help'])(self.help_page)

    def get_role(self, chat_id):
        self.db[1].execute('SELECT role FROM user_roles WHERE chat_id = ?', (chat_id,))
        return self.db[1].fetchone()[0]

    def send_message(self, chat_id, cmd, role, lang_code):
        self.bot.send_message(chat_id, cmd[f'{lang_code}_{role}'])

    def assign_role(self, message):
        if message.text == '/start':
            random.shuffle(self.roles)
            chosen_role = self.roles[0]
            self.db[1].execute('INSERT OR REPLACE INTO user_roles VALUES (?, ?)', (message.chat.id, chosen_role))
            self.db[0].commit()
            self.send_message(message.chat.id, self.cmds[0], chosen_role, message.from_user.language_code)

    def help_page(self, message):
        self.send_message(message.chat.id, self.cmds[1], self.get_role(message.chat.id), message.from_user.language_code)

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

