from discord.ext.commands import Cog, Context, command
from bot import CovidBot


class Ping(Cog):
    def __init__(self, bot: CovidBot):
        self.bot = bot
        self.logger = bot.get_logger(self)

        self.logger.info("initialized")
    
    @command(aliases=["핑"])
    async def ping(self, ctx: Context):
        await ctx.send(str(self.bot.latency * 1000 // 1) + "ms")


def setup(bot: CovidBot):
    bot.add_cog(Ping(bot))
