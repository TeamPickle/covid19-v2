from discord.ext.commands import Cog, Context, command
from bot import CovidBot


class Position(Cog):
    def __init__(self, bot: CovidBot):
        self.bot = bot
        self.db = bot.pickle_db
        self.logger = bot.get_logger(self)

        self.logger.info("initialized")
    
    @command(aliases=["위치지정", "위치설정"])
    async def setpos(self, ctx: Context, *args):
        if len(args) == 2:
            self.db["covid19"]["userloc"].update_one({"_id": ctx.author.id}, {
                "$set": {
                    "loc": " ".join(args)
                }
            }, upsert=True)
            await ctx.send(f"위치 지정이 완료되었습니다. 이제 ``{ctx.prefix}병원`` ``{ctx.prefix}재난문자`` 를 지역 입력 없이 사용할 시 지정한 위치의 정보를 불러옵니다.")
            return
        await ctx.send(f"명령어 사용법 : ``{ctx.prefix}위치지정 [시/도] [시/군/구]``  ex) ``{ctx.prefix}위치지정 서울 서초구``")


def setup(bot: CovidBot):
    bot.add_cog(Position(bot))
