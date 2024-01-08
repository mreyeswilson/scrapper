from controllers.data import Data
from controllers.notify import Notify
from controllers.calendar import Calendar
from datetime import datetime, timedelta
from random import randint
from uuid import uuid4
from controllers.utils import Util
from models.clase import ClassStatus
from models.clase import Clase
from log import logger

class Programmer:

    def __init__(self, data: Data, calendar: Calendar):
        self.data = data
        self.calendar = calendar

    async def start(self, update, code):
        self.update = update
        code = code.upper()
        
        self.usr = self.data.get_user_by_code(code)
        if not self.usr:
            self.usr = self.data.create_user(code)

        await update.message.reply_text(f"👋 Hola *{self.usr.name.split(' ')[0]}*, por favor espera mientras programamos tus 5 clases semanales\.", parse_mode="MarkdownV2")

        self.data._provider.autenticate(code)
        self.data.update_classes()

        now = datetime.now()
        days_until_monday = (0 - now.weekday() + 7) % 7
        monday = now + timedelta(days=days_until_monday)

        week_classes = self.data.get_week_classes(monday.isocalendar().week, self.usr.id)

        if week_classes and len(week_classes["classes"]) > 0:
            raise await Notify.error(update, "Ya tienes clases programadas para esta semana.") 
            

        programmed = await self.__program_clases(monday)

        return programmed

    async def __program_clases(self, start_day) -> list[Clase]:
        programmed = []
        bcheck = f"ADULTOS{self.usr.profile}"
        level_class = f"{self.usr.profile.split(' ')[0]}\/"

        cont = 0
        clase = None
        off = True
        msg = ""

        while len(programmed) < 5:
            day = start_day + timedelta(days=cont)

            if cont > 6:
                if off:
                    await Notify.warn(self.update, msg)
                    raise Exception(
                        "No se encontró un bcheck para ti esta semana, no se puede continuar.")
                cont = 0

            if off:
                classes = self.data.get_clases_by_date(day, bcheck)
            else:
                classes = self.data.get_clases_by_date(day, level_class)

            if len(classes) == 0:
                cont += 1
                bcheck_str = bcheck.replace("-", "\-")
                msg += f'No se encontró una clase *{f"B Check {chr(92)}| {bcheck_str}" if off else level_class}* para el día {day.strftime("%A")}\n'
                continue

            idx = randint(0, len(classes) - 1)
            clase = classes[idx]

            url = clase.url.replace("/13/", f"/{self.usr.id}/")

            clase.link, status = await self.__toggle_class_status(url)

            if status != "ok":
                if status == "maxcupo":
                    clase = None
                    continue

                if status == "off":
                    i = 0
                    off = True
                    break

                if status == "max":
                    raise Exception(
                        "Ya programaste tus 5 clases para esta semana.")

                raise Exception(
                    f"Ocurrió un error al programar la clase: {status}")

            clase.event_id = self.__create_event(clase)
            print(f"Clase {clase.title} | Programada")
            programmed.append(clase)
            off = False
            cont += 1

        return programmed
    
    async def program_oral_test(self, code):
        usr = self.data.get_user_by_code(code)
        classes = self.data.get_oral_test_classes()
        for clase in classes:
            print(clase.title, clase.start)
            url = clase.url.replace("/13/", f"/{usr.id}/")
            clase.link, status = await self.__toggle_class_status(url)
            
            if status == "maxcupo":
                continue
            if status == "ok":
                self.__create_event(clase)
                break

            await Notify.error(self.update, "No se pudo programar el oral test")
            return

    async def cancel_classes(self, code):
        code = code.upper()
        domain = "https://www.beprogrammer.site/beprogrammer/clases/detalle/"
        usr = self.data.get_user_by_code(code)
        if not usr:
            usr = self.data.create_user(code)
        next_monday = Util.get_next_monday()
        week = next_monday.isocalendar().week
        self.data._provider.autenticate(code)
        week_schedule = self.data.get_week_classes(week, usr.id)
        if not week_schedule:
            raise Exception("No tienes clases programadas esta semana.")
        classes = week_schedule["classes"]
        for clase in classes:
            idx = classes.index(clase)
            url = domain + f"{usr.id}/{clase['id']}"
            _, status = await self.__toggle_class_status(url, cancel=True)
            if status == 200:
                try:
                    self.calendar.delete_event(clase["event_id"])
                    clase["cancelled"] = True
                except Exception as e:
                    logger.error(e)

        week_schedule["classes"] = [clase for clase in classes if not clase["cancelled"]]
        self.data.update_schedule(week_schedule)

        return f"Clases canceladas correctamente!"

    async def __toggle_class_status(self, url, cancel = False, code = None):
        if not self.data._provider.code:
            self.data._provider.autenticate(code)

        soup = self.data._provider.create_soup(url)
        form = soup.find("form", attrs={"name": "programar"})

        inputs = form.find_all("input", attrs={
            "type": "hidden"
        })
        
        button = form.find("button", attrs={"type": "submit"})
        event = "programar" if not cancel else "cancelar"

        if cancel and not button:
            await Notify.error(self.update, f"Ya no es posible cancelar la clase - {url.split('/')[-1]}")
            return "", 400

        data = {}
        for item in inputs:
            data[item["name"]] = item["value"]

        data[event] = ""

        res = self.data._provider.send_program_request(url, data=data)

        if not cancel:
            soup = self.data._provider.create_soup(url)
            
            form = soup.find("form", attrs={"name": "programar"})
            link = form.find("a")["href"]
            status = res.url.split("=")[-1]
            return link, status
        
        return "", res.status_code

    def __create_event(self, clase):
        end = clase.start + timedelta(hours=1)
        event = {
            "summary": clase.title,
            "colorId": "9",
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
        return self.calendar.create_event(event)