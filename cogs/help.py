from discord.ext.commands import Cog, Context, command
from bot import CovidBot

class Help(Cog):
    def __init__(self, bot: CovidBot):
        self.bot = bot
        self.logger = bot.get_logger(self)

        self.logger.info("initialized")
    
    @command(aliases=["도움", "도움말"])
    async def help(self, ctx: Context):
        await ctx.send("test")


def setup(bot: CovidBot):
    bot.add_cog(Help(bot))
