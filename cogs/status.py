from discord import Embed
from discord.ext.commands import Cog, Context, command
from bot import CovidBot
import aiohttp
import re

_DISASTER_REGION = ["강원", "경기", "경남", "경북", "광주", "대구", "대전",
                   "부산", "서울", "울산", "인천", "전남", "전북", "제주", "충남", "충북", "세종"]
_DISASTER_ALIAS = {"충청남도": "충남", "충청북도": "충북", "전라북도": "전북", "전라남도": "전남", "경상북도": "경북", "경상남도": "경남"}

class Status(Cog):
    def __init__(self, bot: CovidBot):
        self.bot = bot
        self.logger = bot.get_logger(self)

        self.logger.info("initialized")
    
    @command(aliases=["현황"])
    async def status(self, ctx: Context, *args):
        increase = lambda x: f"▲{x}" if x > 0 else "-0"

        if len(args) == 0:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://coronaboard.kr/") as r:
                    t = eval(re.findall('{"KR":(.+?),"global"', await r.text('utf-8'))[0])
                    t2 = eval(re.findall('"chartTesting":(.+?),"stat', await r.text('utf-8'))[0])
            inf = t["confirmed_acc"][-1]
            cur = t["released_acc"][-1]
            dth = t["death_acc"][-1]
            leapa = t["confirmed"][-1]
            leapb = t["released"][-1]
            leapc = t["death"][-1]
            testing = t2["testing"][-1]
            leapd = testing - t2["testing"][-2]
            per_dth = round(dth/inf*100, 1)
            per_cur = round(cur/inf*100, 1)

            date = t["date"][-1]
            active = t["active"][-1]

            embed = Embed(
                title=f"🇰🇷 대한민국 코로나19 확진 정보 ({date} 기준)",
                description=f"<:nujeok:687907310923677943> **확진자** : {inf}({increase(leapa)})\n" \
                            f"<:wanchi:687907312052076594> **완치** : {cur}({increase(leapb)}) - {per_cur}%\n" \
                            f"<:samang:687907312123510817> **사망** : {dth}({increase(leapc)}) - {per_dth}%\n\n" \
                            f"<:chiryojung:711728328985411616> **치료중** : {active}\n" \
                            f"<:geomsa:687907311301296146> **검사중** : {testing}({increase(leapd)})\n",
                color=0x006699
            )
            embed.set_footer(text="지자체에서 자체 집계한 자료와는 차이가 있을 수 있습니다.")
            embed.set_image(url="https://media.discordapp.net/attachments/687736707902079026/748715852932841502/graph.png")
            await ctx.send(embed=embed)
            return
        elif 1 <= len(args) <= 2:
            u = args[0]
            if u in _DISASTER_ALIAS.keys():
                u = _DISASTER_ALIAS[u]
            
            async with aiohttp.ClientSession() as session:
                async with session.get('https://coronaboard.kr/') as r:
                    res = await r.text('utf-8')
            t: dict = eval('{"CN":' + re.findall(',"CN":(.+?),"North', res)[0] + "}")
            
            arg = " ".join(args)
            if arg in t.values() or arg in ["오스트레일리아", "우리나라", "한국"]:
                country = arg
                if arg == "오스트레일리아":
                    country = "호주"
                elif arg in ["우리나라", "한국"]:
                    country = "대한민국"
                
                cc = {v: k for k, v, in t.items()}[country]
                t = eval(re.findall('"statGlobalNow":(.+?),"stat', res)[0].replace("null", '"null"'))
                v1 = v2 = v3 = leapa = leapb = leapc = 0

                flag = None
                for index in range(len(t)):
                    if t[index]['cc'] == cc:
                        v1 = t[index]['confirmed']
                        v2 = t[index]['released']
                        v3 = t[index]['death']
                        flag = t[index]['flag']
                        per_v2 = round(v2/v1*100, 1)
                        per_v3 = round(v3/v1*100, 1)
                        try:
                            leapa = v1 - t[index]['confirmed_prev']
                            leapb = v2 - t[index]['released_prev']
                            leapc = v3 - t[index]['death_prev']
                        except KeyError:
                            pass
                        break
                if flag == None:
                    await ctx.send("해당 국가에 대한 정보가 없습니다.")
                    return
                title = f"{flag} 국가별 현황 - {arg}"
                v1, v2, v3 = map(lambda x: format(x, ","), (v1, v2, v3))
                embed = Embed(
                    title=title,
                    description=f"<:nujeok:687907310923677943> 확진자 : {v1}명({increase(leapa)})\n" \
                            f"<:wanchi:687907312052076594> 완치 : {v2}명({increase(leapb)}) - {per_v2}%\n" \
                            f"<:samang:687907312123510817> 사망 : {v3}명({increase(leapc)}) - {per_v3}%\n\n",
                    color=0x00bfff
                )
                await ctx.send(embed=embed)
                return
            elif u in _DISASTER_REGION:
                t = eval(re.findall(
                    '"statByKrLocation":(.+?)}],"', res)[0] + "}]")
                cnt = a = c = r = d = leapa = leapc = leapr = leapd = 0
                for item in t:
                    if item['region'] == arg[1]:
                        a = item['active']
                        leapa = a - item['active_prev']
                        c = item['confirmed']
                        leapc = c - item['confirmed_prev']
                        r = item['released']
                        leapr = r - item['released_prev']
                        d = item['death']
                        leapd = d - item['death_prev']
                    cnt += item['confirmed']
                
                embed = Embed(
                    title="시/도 확진자 수 조회 - " + u,
                    description=f"<:nujeok:687907310923677943> **확진자** : {c}명({increase(leapc)}) - {round(c/cnt*100, 1)}\n" \
                            f"<:chiryojung:711728328985411616> **치료중** : {a}명({increase(leapa)})\n" \
                            f"<:wanchi:687907312052076594> 완치 : {r}명({increase(leapr)})\n" \
                            f"<:samang:687907312123510817> 사망 : {d}명({increase(leapd)})\n",
                    color=0xff7f00
                )
                await ctx.send(embed=embed)
                return
        await ctx.send(("전국 통계: ``{prefix}현황``\n" \
                    "시/도 통계: ``{prefix}현황 [시/도]``\n" \
                    "시/군/구 통계: ``{prefix}현황 [시/도] [시/군/구]``\n" \
                    "국가별 통계: ``{prefix}현황 [국가]``").format(prefix=ctx.prefix))

    

def setup(bot: CovidBot):
    bot.add_cog(Status(bot))
