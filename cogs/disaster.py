from discord import Embed
from discord.ext.commands import Cog, Context, command
import aiohttp
from bot import CovidBot
import re
import utils

_DISASTER_REGION = ["전국", "강원", "경기", "경남", "경북", "광주", "대구", "대전",
                  "부산", "서울", "울산", "인천", "전남", "전북", "제주", "충남", "충북", "세종"]
_DISASTER_ALIAS = {"충청남도": "충남", "충청북도": "충북",
                "전라북도": "전북", "전라남도": "전남",
                "경상북도": "경북", "경상남도": "경남"}
_UNSUPPORT_REGION = "지원하지 않는 지역입니다. 다음 지역 중 하나로 다시 시도해주세요:\n" \
                    "``" + " ".join(_DISASTER_REGION) + "``"
_UNABLE_TO_FETCH = "재난문자를 불러올 수 없습니다."


class Disaster(Cog):
    def __init__(self, bot: CovidBot):
        self.bot = bot
        self.logger = bot.get_logger(self)

        self.logger.info("initialized")
    
    @command(name="disaster", aliases=["재난문자"])
    @utils.userpos
    async def disaster(self, ctx: Context, *args):
        if not args:
            await ch.send(f"명령어 사용법 : ``{ctx.prefix}재난문자 [지역]``\n" \
                    "지역 목록 : ``" + " ".join(_DISASTER_REGION) + "``")
            return
        u = args[0]
        if u in _DISASTER_ALIAS.keys():
            u = _DISASTER_ALIAS[u]

        if u not in _DISASTER_REGION:
            await ctx.send(_UNSUPPORT_REGION)
            return
        u1 = _DISASTER_REGION.index(u)

        u1 = "" if u1 == 0 else str(u1).zfill(2)

        async with aiohttp.ClientSession() as session:
            async with session.get(
                    "https://m.search.naver.com/p/csearch/content/nqapirender.nhn?where=m&pkid=258&key=disasterAlert&u1=" + u1) as r:
                source = await r.json()
                source = source["current"]["html"]
        local = re.findall('<em class="area_name">(.+?)</em>', source)
        con = re.findall('<span class="dsc _text">(.+?)</span>', source)
        distime = re.findall('<time datetime="">(.+?)</time>', source)
        if local != [] and con != []:
            embed = Embed(
                title=":pushpin: 재난문자",
                description=u + "지역의 최근 5개 재난문자 목록입니다.",
                color=0xdd2255
            )
            for i in range(5):
                embed.add_field(
                    name=(local[i] + "(" + distime[i] + ")")[:256],
                    value=con[i],
                    inline=False
                )
            await ctx.send(embed=embed)
            return
        else:
            await ctx.send(_UNABLE_TO_FETCH)
            return
    

def setup(bot: CovidBot):
    bot.add_cog(Disaster(bot))
