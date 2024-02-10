import os
import random
import dotenv
import logging
from telegram import Update, Message
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

dotenv.load_dotenv('./.env')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class NonCommandTextFilter(filters.BaseFilter):
    def filter(self, message: Message) -> bool:
        return message.text is not None and not message.text.startswith('/')

non_command_text_filter = NonCommandTextFilter()

waiting_user = None
paired_users = {}
turns = { 'Storyteller': None, 'Listener': None }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global waiting_user
    chat_id = update.effective_chat.id

    if waiting_user is None:
        waiting_user = chat_id
        await context.bot.send_message(chat_id=chat_id, text="Waiting for another user to start a conversation...")
    else:
        roles = ['Storyteller', 'Listener']
        random.shuffle(roles)
        await context.bot.send_message(chat_id=waiting_user, text=f"You've been paired with another user! You are the {roles[0]}.")
        await context.bot.send_message(chat_id=chat_id, text=f"You've been paired with another user! You are the {roles[1]}.")
        paired_users[waiting_user] = chat_id
        paired_users[chat_id] = waiting_user
        turns[roles[0]] = waiting_user
        turns[roles[1]] = chat_id
        waiting_user = None

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global waiting_user, paired_users, turns
    chat_id = update.effective_chat.id

    if chat_id in paired_users:
        paired_chat_id = paired_users[chat_id]
        await context.bot.send_message(chat_id=chat_id, text="You've left the conversation.")
        await context.bot.send_message(chat_id=paired_chat_id, text="Your partner has left the conversation.")
        del paired_users[chat_id]
        del paired_users[paired_chat_id]
        if turns['Storyteller'] == chat_id or turns['Storyteller'] == paired_chat_id:
            turns['Storyteller'] = None
        if turns['Listener'] == chat_id or turns['Listener'] == paired_chat_id:
            turns['Listener'] = None
    elif waiting_user == chat_id:
        waiting_user = None
        await context.bot.send_message(chat_id=chat_id, text="You've left the queue.")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from_chat_id = update.effective_chat.id
    if from_chat_id in paired_users:
        to_chat_id = paired_users[from_chat_id]
        if from_chat_id == turns['Storyteller']:
            reply = update.message.text
            await context.bot.send_message(chat_id=to_chat_id, text=reply)
            turns['Storyteller'], turns['Listener'] = turns['Listener'], turns['Storyteller']
        else:
            await context.bot.send_message(chat_id=from_chat_id, text="It's not your turn yet.")


if __name__ == '__main__':
    TOKEN = os.getenv('TELEGRAM_TOKEN')
    application = ApplicationBuilder().token(TOKEN).build()
    
    start_handler = CommandHandler('start', start)
    application.add_handler(start_handler)
    
    stop_handler = CommandHandler('stop', stop)
    application.add_handler(stop_handler)
    
    text_handler = MessageHandler(non_command_text_filter, handle_text)
    application.add_handler(text_handler)
    
    application.run_polling()
