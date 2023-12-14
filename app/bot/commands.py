from telegram.ext import Application
from bot.handlers.conversations.program import prog_handler

def set_commands(app: Application):

    app.add_handler(prog_handler)

    return app