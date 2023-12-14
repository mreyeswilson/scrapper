from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
from telegram import Update
import re
from controllers.notify import Notify
from controllers.programmer import Programmer
from inject import app

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
        classes = await programmer.start(update, code)
        for clase in classes:
            await update.message.reply_text(f"*{clase.title}*\n\n*Fecha:* {clase.start.date()}\n*Hora:* {clase.start.time()}\n*Link:* {clase.link}", parse_mode="MarkdownV2")
    except:
        return ConversationHandler.END




prog_handler = ConversationHandler(
    entry_points=[CommandHandler("program", program)],
    states={
        CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, code)],
    },
    fallbacks=[]
)