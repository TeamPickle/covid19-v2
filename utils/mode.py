from discord import TextChannel, DMChannel
from discord.ext.commands import Context
from enum import Enum

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