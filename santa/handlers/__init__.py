import enum
import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

import santa.button as Button
from santa import db
from santa.utils import derangement
from santa.handlers.states import State
from .memo import index

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)


reply_keyboard = [[Button.CREATE, Button.ENROLL, Button.MEMO]]
reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
cancel_keyboard = [[Button.BACK]]
cancel_markup = ReplyKeyboardMarkup(cancel_keyboard, one_time_keyboard=True)


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ок", reply_markup=reply_markup)
    return ConversationHandler.END


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
        chat_id=update.effective_chat.id,
        text=f"Комната создана! Номер комнаты: `{santa_id}`",
        parse_mode=ParseMode.MARKDOWN,
    )


async def get_santa_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите номер комнаты:", reply_markup=cancel_markup)
    return State.AWAIT_SANTA_ID


async def enroll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO better feedback and error handling
    if not db.get_user_info(update.effective_chat.id):
        await update.message.reply_text("Сначала заполните информацию о себе")
        return ConversationHandler.END
    santa_id = update.message.text
    try:
        db.enroll(santa_id, update.effective_chat.id)
        logger.info(f"User @{update.effective_chat.username} enrolled into santa: {santa_id}")
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"Вы были успешно добавлены в комнату `{santa_id}`",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN,
        )
        return ConversationHandler.END
    except Exception as e:
        await update.message.reply_text(str(e))
        return State.AWAIT_SANTA_ID


async def members(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        santa_id = update.message.text
        participants = db.get_participants(santa_id, update.effective_chat.id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text=str(participants))
        return ConversationHandler.END
    except PermissionError as e:
        await update.message.reply_text(str(e))
        return State.AWAIT_SANTA_ID


async def santa_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    santa_id = update.message.text
    creator_chat = await context.bot.get_chat(db.get_creator(santa_id))
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"Создатель санты: @{creator_chat.username}")


async def begin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO remove santa somehow?
    if len(context.args) == 1:
        santa_id = context.args[0]
        participants = db.get_participants(santa_id, update.effective_chat.id)
        if len(participants) < 2:
            await context.bot.send_message(chat_id=update.effective_chat.id, text="Слишком мало участников! 😥")
        else:
            who_gifts_who = derangement(participants)
            for sender, receiver in who_gifts_who:
                chat = await context.bot.get_chat(int(receiver))
                await context.bot.send_message(
                    chat_id=int(sender), text=f"Дари @{chat.username}!", parse_mode=ParseMode.MARKDOWN
                )
                await context.bot.send_message(
                    chat_id=int(sender),
                    text=f"Информация от пользователя: @{chat.username}",
                    parse_mode=ParseMode.MARKDOWN,
                )
                await context.bot.send_message(
                    chat_id=int(sender), text=db.get_user_info(int(receiver)), parse_mode=ParseMode.MARKDOWN
                )
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Bad command!")
