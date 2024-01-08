from dotenv import load_dotenv
import multiprocessing
from jobs import start_jobs
load_dotenv()

import os
from bot.commands import set_commands
from telegram.ext import ApplicationBuilder
from log import logger

token = os.environ["TELEGRAM_TOKEN"]
app = ApplicationBuilder().token(token).build()

app = set_commands(app)

jobs_process = multiprocessing.Process(target=start_jobs, name="Schedule jobs process")

if __name__ == "__main__":
    jobs_process.start()

    logger.info("Bot running...")
    app.run_polling()