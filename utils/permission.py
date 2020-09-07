from discord import Member
from discord.ext.commands import Context
from bot import CovidBot
from functools import wraps

def checkadmin(super_admin=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx: Context, *args):
            bot: CovidBot = ctx.bot
            if super_admin:
                if bot.pickle_db["pickle"]["superadmins"].find_one({"_id": str(ctx.author.id)}):
                    await func(self, ctx, *args)
            else:
                if bot.pickle_db["pickle"]["admins"].find_one({"_id": str(ctx.author.id)}):
                    await func(self, ctx, *args)
        return wrapper
    return decorator

def guild_permission(message: str, idx: int=3):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, ctx: Context, *args):
            author: Member = ctx.author
            if author.guild_permissions.value >> (idx - 1) & 1:
                await func(self, ctx, *args)
            else:
                if idx == 3:
                    await ctx.send(message or "서버 관리자만 사용가능한 명령어입니다.")
                else:
                    await ctx.send(message or "명령어를 사용하기 위한 권한이 부족합니다.")
        return wrapper
    return decorator