from discord import Embed
from discord.ext.commands import Cog, Context, command
from bot import CovidBot

_TITLE = "COVID-19(코로나19) 증상 안내"
_DESCRIPTION = "발열(37.5도 이상) \n" \
                "호흡기 증상(기침, 가래, 인후통 등) \n" \
                "폐렴 증상\n" \
                "미각 또는 후각 이상 등\n\n" \
                "위 증상들이 있는 경우 __**병원이나 응급실로 바로 들어가지 마시고, 병원 앞에 마련된 선별 진료소를 통해 진료**__를 받으시기 바랍니다. \n" \
                "감염이 의심된다면 지역보건소 또는 1339, 지역번호+120을 통해 먼저 상담을 받으시기 바랍니다.\n\n" \
                "지역 별 선별 진료소 등 병원 현황은 !병원 커맨드를 이용하여 확인하실 수 있습니다."

class Symptom(Cog):
    def __init__(self, bot: CovidBot):
        self.bot = bot
        self.logger = bot.get_logger(self)

        self.logger.info("initialized")
    
    @command(aliases=["증상"])
    async def symptom(self, ctx: Context):
        embed = Embed(
            title=_TITLE,
            description=_DESCRIPTION,
            color=0x006699
        )
        await ctx.send(embed=embed)


def setup(bot: CovidBot):
    bot.add_cog(Symptom(bot))
