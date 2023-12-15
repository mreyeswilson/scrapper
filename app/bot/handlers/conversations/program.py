from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from telegram import Update
import re
from controllers.notify import Notify
from controllers.programmer import Programmer
from inject import app
from log import logger

CODE = range(1)

async def program(update: Update, context):
    await update.message.reply_text("Ingrese su código:")
    return CODE

async def code(update: Update, context):
    pattern = r"[A-Za-z]{2,3}\-[0-9]{4}"
    code = update.message.text

    if not re.match(pattern, code):
        await Notify.error(update, "Código incorrecto, intente nuevamente")
        return CODE
    try:
        programmer = app.get(Programmer)
        clases = await programmer.start(update, code)
        programmer.data.save_programmed_clases(clases, programmer.usr)

        await Notify.info(update, "Clases programadas correctamente!")
    except Exception as e:
        logger.error(e)
    
    return ConversationHandler.END




prog_handler = ConversationHandler(
    entry_points=[CommandHandler("program", program)],
    states={
        CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, code)],
    },
    fallbacks=[]
)