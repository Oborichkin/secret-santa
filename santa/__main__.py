import os

from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
from dotenv import load_dotenv

from santa.handlers import start, create, enroll, members, begin, States, cancel, get_santa_id, santa_info

load_dotenv()


application = ApplicationBuilder().token(os.environ.get("TOKEN")).build()

start_handler = CommandHandler("start", start)
create_handler = MessageHandler(filters.Text("Create"), create)
begin_handler = CommandHandler("begin", begin)

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

application.add_handlers([start_handler, create_handler, members_handler, begin_handler, enroll_handler, info_handler])

application.run_polling()
