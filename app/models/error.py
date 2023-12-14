from log import logger

class Error:

    def __init__(self, msg, exit=False) -> None:
        self.message = msg
        self.exit = exit
    
    def check(self):
        if exit:
            raise Exception(self.message)
        else:
            logger.warn(self.message)
