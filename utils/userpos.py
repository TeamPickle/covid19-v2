from discord.ext.commands import Context
from bot import CovidBot

def userpos(func):
    async def wrapper(self, ctx: Context, *args):
        bot: CovidBot = ctx.bot
        if len(args) == 0 and (result := bot.pickle_db["covid19"]["userloc"].find_one({"_id": ctx.author.id})):
            args = result["loc"].split(" ")
        await func(self, ctx, *args)
    return wrapper