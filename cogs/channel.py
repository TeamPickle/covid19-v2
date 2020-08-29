from discord import Message, TextChannel, Guild
from discord.ext.commands import Cog, Context, command
from bot import CovidBot
import utils


class Channel(Cog):
    def __init__(self, bot: CovidBot):
        self.bot = bot
        self.db = bot.pickle_db
        self.logger = bot.get_logger(self)

        self.logger.info("initialized")
    
    @command(name="channel", aliases=["채널"])
    @utils.server_command
    async def channel(self, ctx: Context):
        guild: Guild = ctx.guild
        if result := self.db["covid19"]["channels"].find_one({"_id": guild.id}):
            await ctx.send(f"현재 전체공지를 띄우는 채널은 <#{result.channel}> 입니다.")
        else:
            await ctx.send(f"현재 전체공지를 띄우는 채널은 <#{guild.text_channels[0].id}> 입니다.")
    
    @command(name="setchannel", aliases=["채널설정"])
    @utils.server_command
    @utils.guild_permission("서버관리자만 공지 채널을 지정할 수 있습니다.")
    async def set_channel(self, ctx: Context, *args):
        if args:
            msg: Message = ctx.message
            guild: Guild = ctx.guild
            if msg.channel_mentions:
                channel: TextChannel = msg.channel_mentions[0]
                self.db["covid19"]["channels"].update_one(
                    {"_id": guild.id}, {
                        "$set": {
                            "channel": channel.id
                        }
                    }, upsert=True)
                await ctx.send(f"{channel.mention}(이)가 전체공지를 띄울 채널로 설정되었습니다.")
                return
        await ctx.send(f"명령어 사용법 : ``{ctx.prefix}채널설정 #공지``")

    @command(name="noti", aliases=["중요뉴스"])
    @utils.server_command
    @utils.guild_permission("서버관리자만 중요뉴스 받기 옵션을 지정할 수 있습니다.")
    async def noti(self, ctx: Context, *args):
        if args:
            guild: Guild = ctx.guild
            if args[0] == "ㅇ":
                self.db["covid19"]["noti"].insert_one({"_id": guild.id})
                await ctx.send("중요뉴스만 받기 옵션이 설정되었습니다.")
                return
            elif args[0] == "ㄴ":
                self.db["covid19"]["noti"].remove({"_id": guild.id})
                await ctx.send("중요뉴스만 받기 옵션이 해제되었습니다.")
                return
        await ctx.send(f"명령어 사용법 : ``{ctx.prefix}중요뉴스 [ㅇ/ㄴ]``")

    @command(name="dnd", aliases=["방해금지"])
    @utils.server_command
    @utils.guild_permission("서버관리자만 방해금지 모드 옵션을 지정할 수 있습니다.")
    async def dnd(self, ctx: Context, *args):
        if args:
            guild: Guild = ctx.guild
            if args[0] == "ㅇ":
                self.db["covid19"]["dnd"].insert_one({"_id": guild.id})
                await ctx.send("방해금지 모드가 설정되었습니다.")
                return
            elif args[0] == "ㄴ":
                self.db["covid19"]["dnd"].remove({"_id": guild.id})
                await ctx.send("방해금지 모드가 해제되었습니다.")
                return
        await ctx.send(f"명령어 사용법 : ``{ctx.prefix}방해금지 [ㅇ/ㄴ]``")

def setup(bot: CovidBot):
    bot.add_cog(Channel(bot))
