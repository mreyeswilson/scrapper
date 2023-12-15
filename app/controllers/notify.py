

class Notify:

    def __init__(self) -> None:
        pass

    @staticmethod
    async def error(update, msg):
        # add check emoji to the message
        msg = f"❌ {msg}"
        await update.message.reply_text(msg)

    @staticmethod
    async def info(update, *args):
        # add check emoji to the message
        msg = f"ℹ️ {' '.join(args)}"
        await update.message.reply_text(msg)

    @staticmethod
    async def warn(update, *args):
        # add check emoji to the message
        msg = f"⚠️ {' '.join(args)}"
        await update.message.reply_text(msg, parse_mode="MarkdownV2")
