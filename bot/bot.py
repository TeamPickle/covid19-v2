from discord import Game
from discord.ext.commands import AutoShardedBot
import logging

class CovidBot(AutoShardedBot):
    name: str = "CovidBot"
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("command_prefix", "!")
        super().__init__(*args, **kwargs)

        self.logger = logging.getLogger(self.name or self.__class__.__name__)
        formatter = logging.Formatter("[%(asctime)s %(levelname)s] (%(name)s: %(filename)s:%(lineno)d) > %(message)s")

        handler = logging.StreamHandler()
        handler.setLevel('DEBUG')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.setLevel('DEBUG')

    def get_logger(self, cog):
        name = cog.__class__.__name__
        logger = getLogger(name and self.name + "." + name or self.name or self.__class__.__name__)
        logger.setLevel('DEBUG')
        return logger

    def run(self, *args, **kwargs):
        self.logger.info("Starting bot")
        super().run(*args, **kwargs)    

    async def on_ready(self):
        self.logger.info("Bot ready")
        await self.change_presence(
            activity=Game("!도움으로 명령어 확인")
        )
