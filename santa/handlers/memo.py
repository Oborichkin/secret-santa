import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes

from santa import db
from santa.handlers.states import State
import santa.button as Button

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)


memo_keyboard = [[Button.MEMO_SHOW, Button.MEMO_CHANGE, Button.MEMO_DELETE], [Button.BACK]]
memo_markup = ReplyKeyboardMarkup(memo_keyboard, one_time_keyboard=False)


async def index(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Ок", reply_markup=memo_markup)
    return State.MEMO


async def get_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if info := db.get_user_info(update.effective_chat.id):
        await update.message.reply_text(info)
    else:
        await update.message.reply_text("Нет информации")
    return State.MEMO


async def delete_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.remove_user_info(update.effective_chat.id)
    await update.message.reply_text("Информация очищена")
    return State.MEMO


async def prompt_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите информацию о себе:")
    return State.AWAIT_MEMO


async def update_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.add_user_info(update.effective_chat.id, update.message.text_markdown)
    await update.message.reply_text("Информация обновлена")
    return State.MEMO
