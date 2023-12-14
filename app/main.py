from dotenv import load_dotenv
load_dotenv()

import os
from bot.commands import set_commands
from telegram.ext import ApplicationBuilder
from log import logger

token = os.environ["TELEGRAM_TOKEN"]
app = ApplicationBuilder().token(token).build()

app = set_commands(app)

if __name__ == "__main__":
    logger.info("Bot running...")
    app.run_polling()