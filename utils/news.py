from discord import TextChannel, Embed
from discord.ext.commands import Context
from bot import CovidBot
import datetime

async def send(embed: Embed, ctx: Context, imp: bool, iscurrent: bool, channel: TextChannel = None):
    """
    imp: 중요공지 여부
    iscurrent: 현황 변경?
    """
    bot: CovidBot = ctx.bot
    db = bot.pickle_db

    if channel == None:
        channel = ctx.channel

    await bot.get_channel(channel.id).send("start")
    j = 0
    blocklist = list(db["covid19"]["noti"].find())
    blocklist = list(map(lambda x: x['_id'], blocklist))
    dnd = list(db["covid19"]["dnd"].find())
    dnd = list(map(lambda x: x['_id'], dnd))
    chlist = list(db["covid19"]["channels"].find())
    chlist = {item['_id']: item['channel'] for item in chlist}

    good = 7 <= (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).hour < 22

    for guild in bot.guilds:
        try:
            if not((not imp and guild.id in blocklist) or (not good and guild.id in dnd)):
                if guild.id in chlist.keys():
                    await bot.get_channel(chlist[guild.id]).send(embed=embed)
                else:
                    await guild.text_channels[0].send(embed=embed)
        except:
            j += 1
            pass
    i = len(bot.guilds)
    await bot.get_channel(channel.id).send(f"{i - j}/{i}")

    if iscurrent:
        autocall = list(db["covid19"]["autocall"].find())
        autocall = list(map(lambda x: x['_id'], autocall))

        for userid in autocall:
            try:
                await bot.get_user(userid).send(embed=embed)
            except:
                pass
        await bot.get_channel(channel.id).send(f"autocall done: {len(autocall)}")