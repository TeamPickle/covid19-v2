from discord import Game, Message, Embed, TextChannel, Guild, Intents
from discord.ext.commands import AutoShardedBot, Context
from discord.ext.commands.errors import CommandNotFound
import logging, os, random, traceback
from db import PickleDB
import dbl

class CovidBot(AutoShardedBot):
    name = "CovidBot"
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("command_prefix", get_command_prefix)
        intents: Intents = Intents.none()
        intents.messages = True
        super().__init__(*args, help_command=None, intents=intents, **kwargs)

        self.logger = logging.getLogger(self.name or self.__class__.__name__)
        formatter = logging.Formatter("[%(asctime)s %(levelname)s] (%(name)s: %(filename)s:%(lineno)d) > %(message)s")

        handler = logging.StreamHandler()
        handler.setLevel('DEBUG')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

        self.logger.setLevel('DEBUG')

        self.pickle_db = PickleDB()
        self.get_log_channel()

    def get_logger(self, cog):
        name = cog.__class__.__name__
        logger = logging.getLogger(name and self.name + "." + name or self.name or self.__class__.__name__)
        logger.setLevel('DEBUG')
        return logger

    def run(self, *args, **kwargs):
        self.logger.info("Starting bot")
        super().run(*args, **kwargs)

    async def on_ready(self):
        self.logger.info("Bot ready")
        if token := os.getenv("DBL_TOKEN"):
            dbl.DBLClient(self, token)

    async def get_log_channel(self):
      logChannel = os.getenv("LOG_CHANNEL")
      if logChannel:
        self.logChannel = await self.fetch_channel(int(logChannel))

    async def on_command_error(self, ctx: Context, e: Exception):
        if isinstance(e, CommandNotFound):
            return
        if self.logChannel:
            t = "%x" % random.randint(16**7, 16**8)
            embed = Embed(
                title="⚠️ 오류가 발생했습니다.",
                description="[팀 피클 공식 포럼](http://forum.tpk.kr)에 버그를 제보해주세요.\n" \
                    f"코드 ``{t}``를 알려주시면 더 빠른 처리가 가능합니다.",
                color=0xffff00
            )
            await ctx.send(embed=embed)

            content: str = ("Code: {t}\n" \
                    "Requester: {requesterStr}#{requesterS}({requesterNum})\n" \
                    "Message: {message}\n" \
                    "```py\n{trace}```").format(
                        t=t,
                        requesterStr=ctx.author.name,
                        requesterS=ctx.author.discriminator,
                        requesterNum=ctx.author.id,
                        message=ctx.message.content,
                        trace="".join(traceback.format_exception(type(e), e, e.__traceback__))
                    )
            if len(content) > 2000:
                content = content[:1997] + "```"
            await self.logChannel.send(content)
        

def get_command_prefix(bot: CovidBot, msg: Message):
    default = os.getenv("prefix") or "!"
    default = [default + " ", default]
    if type(msg.channel) != TextChannel:
        return default
    if msg.content in map(lambda x: x + "접두사초기화", default):
        return default
    guild: Guild = msg.guild
    if result := bot.pickle_db["covid19"]["prefix"].find_one({"_id": guild.id}):
        prefix = result["prefix"]
        return [prefix + " ", prefix]
    return default