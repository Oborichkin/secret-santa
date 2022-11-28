import os

from telegram.ext import ApplicationBuilder, CommandHandler
from dotenv import load_dotenv
load_dotenv()

from santa.handlers import start, create, enroll, members, begin


application = ApplicationBuilder().token(os.environ.get("TOKEN")).build()

start_handler = CommandHandler('start', start)
create_handler = CommandHandler('create', create)
enroll_handler = CommandHandler('enroll', enroll)
members_handler = CommandHandler('members', members)
begin_handler = CommandHandler('begin', begin)

application.add_handlers([
    start_handler,
    create_handler,
    enroll_handler,
    members_handler,
    begin_handler
])

application.run_polling()
