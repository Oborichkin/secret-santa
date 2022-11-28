import os

from telegram.ext import ApplicationBuilder, CommandHandler, ConversationHandler, MessageHandler, filters
from dotenv import load_dotenv
load_dotenv()

from santa.handlers import start, create, enroll, members, begin, States, cancel, begin_enroll


application = ApplicationBuilder().token(os.environ.get("TOKEN")).build()

start_handler = CommandHandler('start', start)
create_handler = MessageHandler(filters.Text("Create"), create)
members_handler = CommandHandler('members', members)
begin_handler = CommandHandler('begin', begin)

enroll_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Text("Enroll"), begin_enroll)],
    states={
        States.ENROLLING: [MessageHandler(filters.TEXT & ~filters.Text("Cancel"), enroll)]
    },
    fallbacks=[MessageHandler(filters.Text("Cancel"), cancel)]
)

application.add_handlers([
    start_handler,
    create_handler,
    members_handler,
    begin_handler
])
application.add_handler(enroll_handler)

application.run_polling()
