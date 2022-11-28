import enum
import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

from santa import db
from santa.utils import derangement

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)


reply_keyboard = [["Create", "Enroll"], ["Cancel"]]
reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)


class States(enum.Enum):
    IDLE = 0
    ENROLLING = 1


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO Make a more sensible message
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!", reply_markup=reply_markup
    )


async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO better feedback and error handling
    santa_id = db.new_santa(update.effective_chat.id)
    logger.info(f"User @{update.effective_chat.username} generated new santa: {santa_id}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=f"Created! `{santa_id}`", parse_mode=ParseMode.MARKDOWN
    )


async def begin_enroll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Enter Santa ID:")
    return States.ENROLLING


async def enroll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO better feedback and error handling
    santa_id = update.message.text
    try:
        db.enroll(santa_id, update.effective_chat.id)
        logger.info(f"User @{update.effective_chat.username} enrolled into santa: {santa_id}")
        await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Enrolled! into `{santa_id}`")
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(str(e))
        return States.ENROLLING


async def members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO print usernames
    if len(context.args) == 1:
        santa_id = context.args[0]
        participants = db.get_participants(santa_id, update.effective_chat.id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=str(participants))
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Bad command!")


async def begin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO remove santa somehow?
    if len(context.args) == 1:
        santa_id = context.args[0]
        participants = db.get_participants(santa_id, update.effective_chat.id)
        if len(participants) < 2:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Too little participants!")
        else:
            who_gifts_who = derangement(participants)
            for sender, receiver in who_gifts_who:
                chat = await context.bot.get_chat(int(receiver))
                await context.bot.send_message(
                    chat_id=int(sender), text=f"Дари @{chat.username}!", parse_mode=ParseMode.MARKDOWN
                )
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Bad command!")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancels and ends the conversation."""
    logger.info(f"User {update.effective_chat.username} enrolling.")
    await update.message.reply_text("Enrolling cancelled!")
    return ConversationHandler.END
