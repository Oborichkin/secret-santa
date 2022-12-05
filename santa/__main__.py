import os

from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
from dotenv import load_dotenv

from santa.handlers import start, create, enroll, members, begin, get_santa_id, santa_info, reset
from santa.handlers.memo import get_user_info, delete_user_info, update_user_info, prompt_user_info, index
from santa.handlers.room import list_participants
from santa.handlers.states import State
import santa.button as Button

load_dotenv()


application = ApplicationBuilder().token(os.environ.get("TOKEN")).build()


def make_santa_id_convo_handler(entry_text, handler):
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Text(entry_text), get_santa_id)],
        states={State.AWAIT_SANTA_ID: [MessageHandler(filters.TEXT & ~filters.Text(Button.BACK), handler)]},
        fallbacks=[MessageHandler(filters.Text(Button.BACK), reset)],
    )


enroll_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Text(Button.ENROLL), get_santa_id)],
    states={State.AWAIT_SANTA_ID: [MessageHandler(filters.TEXT & ~filters.Text(Button.BACK), enroll)]},
    fallbacks=[MessageHandler(filters.Text(Button.BACK), reset)],
)

members_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Text(Button.LIST), get_santa_id)],
    states={State.AWAIT_SANTA_ID: [MessageHandler(filters.TEXT & ~filters.Text(Button.BACK), members)]},
    fallbacks=[MessageHandler(filters.Text(Button.BACK), reset)],
)

info_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Text("Info"), get_santa_id)],
    states={State.AWAIT_SANTA_ID: [MessageHandler(filters.TEXT & ~filters.Text(Button.BACK), santa_info)]},
    fallbacks=[MessageHandler(filters.Text(Button.BACK), reset)],
)

memo_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Text(Button.MEMO), index)],
    states={
        State.MEMO: [
            MessageHandler(filters.Text(Button.MEMO_SHOW), get_user_info),
            MessageHandler(filters.Text(Button.MEMO_CHANGE), prompt_user_info),
            MessageHandler(filters.Text(Button.MEMO_DELETE), delete_user_info),
        ],
        State.AWAIT_MEMO: [MessageHandler(filters.TEXT & ~filters.Text(Button.BACK), update_user_info)],
    },
    fallbacks=[MessageHandler(filters.Text(Button.BACK), reset)],
)

application.add_handlers(
    [
        CommandHandler("start", start),
        CommandHandler("begin", begin),
        CommandHandler("list", list_participants),
        MessageHandler(filters.Text(Button.CREATE), create),
        make_santa_id_convo_handler(Button.LIST, members),
        make_santa_id_convo_handler(Button.ENROLL, enroll),
        make_santa_id_convo_handler("Info", santa_info),
        memo_handler,
        MessageHandler(filters.Text(Button.BACK), reset),
    ]
)

application.run_polling()
