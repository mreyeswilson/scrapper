

class Notify:

    def __init__(self) -> None:
        pass

    @staticmethod
    async def error(update, msg):
        # add check emoji to the message
        msg = f"❌ {msg}"
        await update.message.reply_text(msg)
