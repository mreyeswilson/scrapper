from inject import app
from controllers.programmer import Programmer
import asyncio

def program_oral_test():
    programmer = app.get(Programmer)

    users = programmer.data.get_users()
    for user in users:
        programmer.data._provider.autenticate(user.code)
        attendance = programmer.data._provider.get_attendance()
        b_attendance = [att for att in attendance if "B Check" in att["class"] and att["status"] == "SH"]
        oral_attendance = [att for att in attendance if "ORAL TEST" in att["class"] and att["status"] == "SH"]
        programmed_oral = [att for att in attendance if "ORAL TEST" in att["class"] and att["status"] == ""]

        # Validamos si ya hay un oral test programado
        if len(programmed_oral) > 0:
            return

        if not (len(b_attendance) == 3 * len(oral_attendance)):
            if len(b_attendance) % 3 == 0:
                asyncio.run(programmer.program_oral_test(user.code))
        print("Todo bien")