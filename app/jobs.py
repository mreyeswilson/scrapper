import time
import schedule
from handlers.oral_test import program_oral_test
from handlers.check_profile import update_profile
from log import logger


schedule.every().hour.do(program_oral_test)
schedule.every().hour.do(update_profile)

def start_jobs():
    logger.info("Starting jobs...")
    while True:
        schedule.run_pending()
        time.sleep(1)