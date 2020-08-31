from discord import Message, File, Embed
from discord.ext.commands import Cog, Context, command
from bot import CovidBot
import matplotlib
import aiohttp, re, datetime, os, asyncio, requests
import utils


class Admin(Cog):
    def __init__(self, bot: CovidBot):
        self.bot = bot
        self.db = bot.pickle_db
        self.logger = bot.get_logger(self)

        matplotlib.rc('font', family="NanumGothic")

        if not os.path.exists("botdata"):
            os.mkdir("botdata")

            res = requests.get('https://coronaboard.kr/').text
            t = eval(re.findall(
                'Global":{"KR":(.+?),"global"', res)[0])
            with open("./botdata/patient.txt", "w") as f:
                f.write(str(t))
            

        self.logger.info("initialized")

    
    @command(name="send", aliases=["전송"])
    @utils.checkadmin()
    async def send(self, ctx: Context, *args):
        if not args:
            await ctx.send("!전송 <속보|뉴스|해외|확진|사망>")
            return
        def check(mes: Message):
            return mes.author == ctx.author and mes.channel == ctx.channel
        
        try:
            await ctx.send("전송할 내용을 입력해주세요.")

            mes: Message = await ctx.bot.wait_for('message', check=check, timeout=300)

            typ = args[0]
            if typ == "속보":
                title = "<:sokbo:687907311875915845> 속보"
                color = 0xff4848
            elif typ == "뉴스":
                title = "<:gisa:687907312102670346> 뉴스"
                color = 0x6699ff
            elif typ == "해외":
                title = "<:waeguk:687907310982791183> 해외뉴스"
                color = 0x9966ff
            elif typ == "확진":
                title = "<:nujeok:687907310923677943> 추가 확진자 발생"
                color = 0xff7c80
            elif typ == "사망":
                title = "<:samang:687907312123510817> 추가 사망자 발생"
                color = 0x222222
            else:
                title = "📢 전체공지"
                color = 0x555555
            embed = Embed(
                title=title,
                description=mes.content,
                color=color
            )

            await ctx.send(embed=embed)
            await ctx.send("위와 같이 공지 메세지를 전송하시겠습니까? [ㅇ/ㄴ]")
            send_accept = await self.bot.wait_for('message', check=check, timeout=100)

            if send_accept.content == "y" or send_accept.content == "ㅇ" or send_accept.content == "d":
                await utils.send(embed, ctx, False)
            else:
                await ctx.send("전송이 취소되었습니다.")
        except asyncio.TimeoutError:
            await ctx.send("시간이 만료되었습니다.")
    
    @command(name="graph")
    @utils.checkadmin()
    async def graph(self, ctx: Context):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://coronaboard.kr/') as r:
                res = await r.text('utf-8')
        t = eval(re.findall(
            'Global":{"KR":(.+?),"global"', res)[0])

        with open("./botdata/patient.txt", 'r') as f:
            pat = f.read()

        if pat != str(t):
            with open("./botdata/patient.txt", 'w') as f:
                f.write(str(t))
        
        await utils.makeGraph(t, self.bot)
        graphmsg: Message = await ctx.send(file=File("./botdata/graph.png"))
        self.db["covid19"]["graphs"].insert_one({
            "_id": graphmsg.attachments[0].url,
            "createdAt": datetime.datetime.utcnow()
        })

    @command(name="yna", aliases=["연합뉴스"])
    @utils.checkadmin()
    async def yna(self, ctx: Context, *args):
        embed = Embed(
            title="<:sokbo:687907311875915845> 속보",
            description=" ".join(args),
            color=0xff4848
        )
        embed.set_footer(text="위 뉴스는 자동으로 보내진 속보입니다.")
        await utils.send(embed, ctx, False)
        

def setup(bot: CovidBot):
    bot.add_cog(Admin(bot))
