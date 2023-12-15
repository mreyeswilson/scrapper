from datetime import datetime, timedelta
from bs4 import BeautifulSoup

class Util:

    @staticmethod
    def get_next_monday():
        now = datetime.now()
        days_until_next_monday = (0 - now.weekday() + 7) % 7
        return now + timedelta(days=days_until_next_monday)
