from telegram.ext import Application
from bot.handlers.conversations.program import prog_handler
from bot.handlers.conversations.cancel import cancel_handler

def set_commands(app: Application):

    app.add_handler(prog_handler)
    app.add_handler(cancel_handler)

    return app