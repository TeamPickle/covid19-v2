from discord import Member
from discord.ext.commands import Context
from bot import CovidBot

def checkadmin(super_admin=False):
    def decorator(func):
        async def wrapper(self, ctx: Context, *args):
            bot: CovidBot = ctx.bot
            if super_admin:
                if bot.pickle_db.pickle.superadmins.find_one({"_id": str(ctx.author.id)}):
                    await func(self, ctx, *args)
            else:
                if bot.pickle_db.pickle.admins.find_one({"_id": str(ctx.author.id)}):
                    await func(self, ctx, *args)
        return wrapper
    return decorator

def guild_permission(idx: int=3):
    def decorator(func):
        async def wrapper(self, ctx: Context, *args):
            author: Member = ctx.author
            if author.guild_permissions.value >> (idx - 1) & 1:
                await func(self, ctx, *args)
        return wrapper
    return decorator