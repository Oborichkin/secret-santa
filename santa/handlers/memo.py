import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from santa import db
from santa.handlers.states import State
import santa.button as Button

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)


memo_keyboard = [[Button.MEMO_CHANGE, Button.MEMO_SHOW], [Button.BACK]]
memo_markup = ReplyKeyboardMarkup(memo_keyboard, one_time_keyboard=False)

memo_index = f"""В этом разделе можно заполнить или просмотреть информацию о себе.
Нажми «{Button.MEMO_CHANGE}» если еще не вносил информацию.
После внесения информации, убедись, что она сохранена, нажав «{Button.MEMO_SHOW}».
"""

memo_prompt = """Заполни информацию о себе. Одним сообщением напиши:
1. 🪪 Имя Фамилию
2. 🏬 Свой отдел
3. 📜 Список желаний
"""


async def index(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"{update.effective_chat.id} enters memo info")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=memo_index, reply_markup=memo_markup)
    return State.MEMO


async def get_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"{update.effective_chat.id} looks info")
    if info := db.get_user_info(update.effective_chat.id):
        await update.message.reply_text(info)
    else:
        await update.message.reply_text("Нет информации")
    return State.MEMO


async def delete_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"{update.effective_chat.id} removes information about himself")
    db.remove_user_info(update.effective_chat.id)
    await update.message.reply_text("Информация очищена")
    return State.MEMO


async def prompt_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"{update.effective_chat.id} promting for info")
    await update.message.reply_text(memo_prompt, parse_mode=ParseMode.MARKDOWN)
    return State.AWAIT_MEMO


async def update_user_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    db.add_user_info(update.effective_chat.id, update.message.text_markdown)
    logger.info(f"{update.effective_chat.id} entered:\n {update.message.text_markdown}\n")
    await update.message.reply_text("Информация обновлена")
    return State.MEMO
