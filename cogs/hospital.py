from discord import Embed
from discord.ext.commands import Cog, Context, command
from bot import CovidBot
import re, aiohttp
import utils


class Hospital(Cog):
    def __init__(self, bot: CovidBot):
        self.bot = bot
        self.logger = bot.get_logger(self)

        self.logger.info("initialized")
    
    @command(name="hospital", aliases=["병원"])
    @utils.userpos
    async def hospital(self, ctx: Context, *args):
        if len(args) >= 2:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://happycastle.club/hospital?city={0}&gu={1}".format(args[0], args[1])) as r:
                    status_code = r.status
                    res = await r.json()
            if status_code == 404:
                await ctx.send("해당 지역에서 병원을 찾을 수 없습니다.")
            elif status_code == 200:
                t = ""
                for hos in res:
                    t += "{0} {1} [지도](https://www.google.co.kr/maps/search/{2})\n".format(
                        re.sub(r"\*\(.*\)", "💉",
                                hos["name"]), hos["number"],
                        re.sub(r"\*\(.*\)", "", hos["name"]).replace(" ", "+"))
                embed = Embed(
                    description=t[:2048],
                    color=0x92f0f2
                )
                embed.set_footer(text="주사기 아이콘 : 검체채취 가능 병원")
                await ctx.send(embed=embed)
            elif res.status_code == 5000:
                await ctx.send("API Error")
        else:
            await ctx.send("명령어 사용법 : ``{prefix}병원 [시/도] [시/군/구]``".format(prefix=ctx.prefix))


def setup(bot: CovidBot):
    bot.add_cog(Hospital(bot))
