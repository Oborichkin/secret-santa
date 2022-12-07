import logging

from telegram import Update
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

from santa import db


logger = logging.getLogger(__name__)


async def list_participants(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"{update.effective_chat.id} executes /list")
    if len(context.args) == 1:
        santa_id = context.args[0]
        try:
            participants = db.get_participants(santa_id, update.effective_chat.id)
            for chat_id in participants:
                userinfo = db.get_user_info(chat_id)
                chat = await context.bot.get_chat(chat_id)
                logger.debug(f"@{chat.username} info:\n{userinfo}\n\n")
                await context.bot.send_message(chat_id=update.effective_chat.id, text=db.get_user_info(chat_id))
        except Exception as e:
            await context.bot.send_message(chat_id=update.effective_chat.id, text=str(e))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Bad command!")
