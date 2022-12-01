import enum
import logging

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from telegram.constants import ParseMode

import santa.button as Button
from santa import db
from santa.utils import derangement2
from santa.handlers.states import State
from .memo import index

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

logger = logging.getLogger(__name__)


reply_keyboard = [[Button.MEMO, Button.ENROLL, Button.CREATE]]
reply_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
cancel_keyboard = [[Button.BACK]]
cancel_markup = ReplyKeyboardMarkup(cancel_keyboard, one_time_keyboard=True)


start_markup = f"""Привет! Чтобы принять участие в Тайном Санте:
🔹В разделе «{Button.MEMO}» заполни необходимую информацию
🔹Нажми «участвовать» и введи номер комнаты (в official announcement в slack)
🔹когда закончится срок регистрации, тебе придёт сообщение с информацией о человеке, которому ты подготовишь подарок 🎁

Все подробности есть в Slack. Веселой игры! 🎅"""


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"{update.effective_chat.id} resets state")
    await update.message.reply_text("Возврат в начальное меню", reply_markup=reply_markup)
    return ConversationHandler.END


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"{update.effective_chat.id} executes /start")
    await context.bot.send_message(
        chat_id=update.effective_chat.id, text=start_markup, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN
    )


async def create(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO better feedback and error handling
    logger.info(f"{update.effective_chat.id} tries to create new room")
    santa_id = db.new_santa(update.effective_chat.id)
    logger.info(f"User @{update.effective_chat.username} generated new room: {santa_id}")
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"Комната создана! Номер комнаты: `{santa_id}`",
        parse_mode=ParseMode.MARKDOWN,
    )


async def get_santa_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"prompring {update.effective_chat.id} for room id")
    await update.message.reply_text("Введите номер комнаты:", reply_markup=cancel_markup)
    return State.AWAIT_SANTA_ID


memo_warning = f"""Для добавления в комнату сначала необходимо заполнить информацию о себе:
1. Перейдите в раздел "{Button.MEMO}"
2. Выберите "{Button.MEMO_CHANGE}"
3. Повторите регистрацию в команте
"""


async def enroll(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # TODO better feedback and error handling
    if not db.get_user_info(update.effective_chat.id):
        logger.info(f"warning {update.effective_chat.id} about info abscense")
        await update.message.reply_text(memo_warning)
        return ConversationHandler.END
    santa_id = update.message.text
    try:
        logger.info(
            f"User @{update.effective_chat.username} from id {update.effective_chat.id} enrolled into: {santa_id}"
        )
        db.enroll(santa_id, update.effective_chat.id)
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
            who_gifts_who = derangement2(participants)
            for sender, receiver in who_gifts_who.items():
                await context.bot.send_message(
                    chat_id=sender,
                    text="Информация от получателя:",
                    parse_mode=ParseMode.MARKDOWN,
                )
                await context.bot.send_message(
                    chat_id=sender, text=db.get_user_info(receiver), parse_mode=ParseMode.MARKDOWN
                )
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="Bad command!")
