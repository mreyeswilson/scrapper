

class Event:

    def __init__(self, **kwargs):
        self.summary = kwargs.get('summary')
        self.location = kwargs.get('location')
        self.description = kwargs.get('description')
        self.start = kwargs.get('start')
        self.end = kwargs.get('end')
        self.reminders = kwargs.get('reminders', {
            "useDefault": False,
            "overrides": []
        })

        