from inject import app
from controllers.programmer import Programmer


def update_profile():
    programmer = app.get(Programmer)
    programmer.data.update_profile()

    