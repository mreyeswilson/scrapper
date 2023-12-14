from controllers.data import Data
from controllers.notify import Notify
from typing import List
from models.clase import Clase
from controllers.calendar import Calendar

from selenium.webdriver import Chrome
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By

from datetime import datetime, timedelta
from random import randint
from uuid import uuid4

class Programmer:

    def __init__(self, data: Data, calendar: Calendar):
        self.data = data
        self.calendar = calendar
        self.driver = Chrome(
            service=ChromeService(ChromeDriverManager().install())
        )

    async def start(self, update, code):
        code = code.upper()
        try:
            usr = self.data.get_user_by_code(code)
            if not usr:
                usr = self.data.create_user(code)

            await update.message.reply_text(f"👋 Hola *{usr.name.split(' ')[0]}*, por favor espera mientras programamos tus 5 clases semanales\.", parse_mode="MarkdownV2")

            self.data._provider.autenticate(code)
            self.data.update_classes()

            programmed: List[Clase] = []

            self.driver.get(self.data._provider.DOMAIN)
            for key, value in self.data._provider.cookies.items():
                self.driver.add_cookie({"name": key, "value": value})

            now = datetime.now()
            days_until_monday = (0 - now.weekday() + 7) % 7
            monday = now + timedelta(days=days_until_monday)
            
            bcheck = f"ADULTOS{usr.profile}"
            level_class = f"{usr.profile.split(' ')[0]}\/"

            for i in range(5):
                clase = None
                day = monday + timedelta(days=i)

                if day.weekday() == 0:
                    classes = self.data.get_clases_by_date(day, bcheck)
                else:
                    classes = self.data.get_clases_by_date(day, level_class)

                if len(classes) == 0:
                    raise Exception("No hay clases disponibles.")

                while not clase:
                    idx = randint(0, len(classes) - 1)
                    clase = classes[idx]

                    url = clase.url.replace("/13/", f"/{usr.id}/")
                    
                    self.driver.get(url)

                    button = self.driver.find_element(
                    by=By.CSS_SELECTOR, value="[type=submit]")

                    if not button:
                        continue
                    
                    button.click()

                    response = self.driver.execute_script("return window.performance.getEntries()[0]")
                    status = response["name"].split("=")[-1]

                        
                    if "maxcupo" in status:
                        clase = None
                        classes.pop(idx)
                        continue

                    if "max" in status:
                        clase = None
                        raise Exception("Ya programaste todas tus clases esta semana.")
                    
                    if not "ok" in status:
                        clase = None
                        raise Exception(f"Error: No se pudo programar la asesoría - {status}")
                    
                    self.data._provider.get_class_link(url)

                    end = clase.start + timedelta(hours=1)
                    
                    event = {
                        "summary": clase.title,
                        "description": clase.link,
                        "start": {
                            "dateTime": clase.start.isoformat(),
                            "timeZone": "America/Bogota"
                        },
                        "end": {
                            "dateTime": end.isoformat(),
                            "timeZone": "America/Bogota"
                        },
                        "reminders": {
                            "useDefault": False,
                            "overrides": [
                                {
                                    "method": "popup",
                                    "minutes": 10
                                }
                            ]
                        },
                        "conferenceData": {
                            "createRequest": {
                                "requestId": str(uuid4().hex),
                                "conferenceSolutionKey": {
                                    "type": "hangoutsMeet"
                                }
                            },
                            "entryPoints": [
                                {"entryPointType": "video", "uri": clase.link},
                            ],
                        }
                    }
                    
                    self.calendar.create_event(event)
                    programmed.append(clase)

            self.driver.quit()
            return classes
        except Exception as e:
            await Notify.error(update, e)
            return []

