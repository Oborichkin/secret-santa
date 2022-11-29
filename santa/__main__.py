import os

from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
from dotenv import load_dotenv

from santa.handlers import start, create, enroll, members, begin, States, cancel, get_santa_id, santa_info

load_dotenv()


application = ApplicationBuilder().token(os.environ.get("TOKEN")).build()


def make_santa_id_convo_handler(entry_text, handler):
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Text(entry_text), get_santa_id)],
        states={States.AWAIT_SANTA_ID: [MessageHandler(filters.TEXT & ~filters.Text("Cancel"), handler)]},
        fallbacks=[MessageHandler(filters.Text("Cancel"), cancel)],
    )


enroll_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Text("Enroll"), get_santa_id)],
    states={States.AWAIT_SANTA_ID: [MessageHandler(filters.TEXT & ~filters.Text("Cancel"), enroll)]},
    fallbacks=[MessageHandler(filters.Text("Cancel"), cancel)],
)

members_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Text("List"), get_santa_id)],
    states={States.AWAIT_SANTA_ID: [MessageHandler(filters.TEXT & ~filters.Text("Cancel"), members)]},
    fallbacks=[MessageHandler(filters.Text("Cancel"), cancel)],
)

info_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Text("Info"), get_santa_id)],
    states={States.AWAIT_SANTA_ID: [MessageHandler(filters.TEXT & ~filters.Text("Cancel"), santa_info)]},
    fallbacks=[MessageHandler(filters.Text("Cancel"), cancel)],
)

application.add_handlers(
    [
        CommandHandler("start", start),
        MessageHandler(filters.Text("Create"), create),
        CommandHandler("begin", begin),
        make_santa_id_convo_handler("List", members),
        make_santa_id_convo_handler("Enroll", enroll),
        make_santa_id_convo_handler("Info", santa_info),
    ]
)

application.run_polling()
