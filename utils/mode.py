from discord import TextChannel, DMChannel
from discord.ext.commands import Context
from enum import Enum
from functools import wraps

class Mode(Enum):
    SERVER = 0
    DM = 1
    UNKNOWN = 2

def get_mode(ctx: Context) -> Mode:
    if type(ctx.channel) == TextChannel:
        mode = Mode.SERVER
    elif type(ctx.channel) == DMChannel:
        mode = Mode.DM
    else:
        mode = Mode.UNKNOWN
    return mode

def server_command(func):
    @wraps(func)
    async def wrapper(self, ctx: Context, *args):
        if get_mode(ctx) != Mode.SERVER:
            await ctx.send("해당 명령어는 서버 채널에서 이용하실 수 있습니다. 아래 링크를 클릭하여 봇을 내 서버에 초대해 보세요!\nhttp://covid19bot.tpk.kr")
        else:
            await func(self, ctx, *args)
    return wrapper

def dm_command(func):
    @wraps(func)
    async def wrapper(self, ctx: Context, *args):
        if get_mode(ctx) != Mode.DM:
            await ch.send("해당 명령어는 개인 채널에서만 사용하실 수 있습니다.")
        else:
            await func(self, ctx, *args)
    return wrapper