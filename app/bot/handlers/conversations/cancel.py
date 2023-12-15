from telegram import Update
from inject import app
from controllers.programmer import Programmer
import re
from controllers.notify import Notify
from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters

CODE = range(1)

async def cancel(update: Update, context):
    await update.message.reply_text("Ingrese su código:")
    return CODE

async def code(update: Update, context):
    pattern = r"[A-Za-z]{2,3}\-[0-9]{4}"
    code = update.message.text

    if not re.match(pattern, code):
        await Notify.error(update, "Código incorrecto, intente nuevamente")
        return CODE

    await update.message.reply_text("Espera un momento, mientras cancelamos tus clases.")
    programmer = app.get(Programmer)

    try:
        result = await programmer.cancel_classes(code)
        await Notify.info(update, result)
    except Exception as e:
        await Notify.error(update, e)

    return ConversationHandler.END


cancel_handler = ConversationHandler(
    entry_points=[CommandHandler("cancel_classes", cancel)],
    states={
        CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, code)]
    },
    fallbacks=[]
)