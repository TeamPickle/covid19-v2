from discord import Message, File, Embed
from discord.ext.commands import Cog, Context, command
from bot import CovidBot
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# from matplotlib import font_manager
import aiohttp, re, datetime, os, asyncio, requests
import utils


class Admin(Cog):
    def __init__(self, bot: CovidBot):
        self.bot = bot
        self.db = bot.pickle_db
        self.logger = bot.get_logger(self)

        # self.fontprop = font_manager.FontProperties(fname="./malgunbd.TTF").get_name()

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
                await ctx.send("중요? [ㅇ/ㄴ]")
                send_accept = await self.bot.wait_for('message', check=check, timeout=100)

                if send_accept.content == "y" or send_accept.content == "ㅇ" or send_accept.content == "d":
                    await self.__send(embed, ctx, True, False)
                    # if typ in ["속보", "뉴스", "해외", "확진", "사망"]:
                        # with open('./botdata/news.txt', 'rb') as f:
                        #     news = pickle.load(f)
                        # now = (datetime.datetime.utcnow(
                        # ) + datetime.timedelta(hours=9)).strftime('%m,%d,%H,%M').split(',')
                        # yy = now[2] + ":" + now[3]
                        # if int(now[2]) >= 12:
                        #     yy = "오후 " + yy
                        # else:
                        #     yy = "오전 " + yy
                        # news.append(
                        #     [now[0]+"월 "+now[1]+"일", yy, typ, mes.content])
                        # with open('./botdata/news.txt', 'wb') as f:
                        #     pickle.dump(
                        #         news, f, protocol=pickle.HIGHEST_PROTOCOL)

                elif send_accept.content == "s" or send_accept.content == "ㄴ" or send_accept.content == "n":
                    await self.__send(embed, ctx, False, False)
                    # if typ in ["속보", "뉴스", "해외", "확진", "사망"]:
                        # with open('./botdata/news.txt', 'rb') as f:
                        #     news = pickle.load(f)
                        # now = (datetime.datetime.utcnow(
                        # ) + datetime.timedelta(hours=9)).strftime('%m,%d,%H,%M').split(',')
                        # yy = now[2] + ":" + now[3]
                        # if int(now[2]) >= 12:
                        #     yy = "오후 " + yy
                        # else:
                        #     yy = "오전 " + yy
                        # news.append(
                        #     [now[0]+"월 "+now[1]+"일", yy, typ, mes.content])
                        # with open('./botdata/news.txt', 'wb') as f:
                        #     pickle.dump(
                        #         news, f, protocol=pickle.HIGHEST_PROTOCOL)
                else:
                    await ctx.send("전송이 취소되었습니다.")
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
        
        await makeGraph(t)
        graphmsg: Message = await ctx.send(file=File("./botdata/graph.png"))
        self.db["covid19"]["graphs"].insert_one({
            "_id": graphmsg.attachments[0].url,
            "createdAt": datetime.datetime.utcnow()
        })

    @command(name="연합뉴스")
    @utils.checkadmin()
    async def yna(self, ctx: Context, *args):
        embed = Embed(
            title="<:sokbo:687907311875915845> 속보",
            description=" ".join(args),
            color=0xff4848
        )
        embed.set_footer(text="위 뉴스는 자동으로 보내진 속보입니다.")
        await self.__send(embed, ctx, False, False)
        

    async def __send(self, embed: Embed, ctx: Context, imp: bool, iscurrent: bool):
        """
        imp: 중요공지 여부
        iscurrent: 현황 변경?
        """
        await ctx.send("start")
        j = 0
        blocklist = list(self.db["covid19"]["noti"].find())
        blocklist = list(map(lambda x: x['_id'], blocklist))
        dnd = list(self.db["covid19"]["dnd"].find())
        dnd = list(map(lambda x: x['_id'], dnd))
        chlist = list(self.db["covid19"]["channels"].find())
        chlist = {item['_id']: item['channel'] for item in chlist}

        good = 7 <= (datetime.datetime.utcnow() + datetime.timedelta(hours=9)).hour < 22

        for guild in self.bot.guilds:
            try:
                if not((not imp and guild.id in blocklist) or (not good and guild.id in dnd)):
                    if guild.id in chlist.keys():
                        await self.bot.get_channel(chlist[guild.id]).send(embed=embed)
                    else:
                        await guild.text_channels[0].send(embed=embed)
            except Exception:
                j += 1
                raise
        i = len(self.bot.guilds)
        await ctx.send(f"{i - j}/{i}")

        if iscurrent:
            autocall = list(self.db["covid19"]["autocall"].find())
            autocall = list(map(lambda x: x['_id'], autocall))

            for userid in autocall:
                try:
                    await self.bot.get_user(userid).send(embed=embed)
                except Exception:
                    raise
            await ctx.send(f"autocall done: {len(autocall)}")
            


async def makeGraph(t):
    dtnow = datetime.datetime.now()
    x = list(datetime.datetime(dtnow.year, int(i.split('.')[0]), int(
        i.split('.')[1])) for i in t['date'][-10:])
    y1 = list(int(i) for i in t['confirmed'][-10:])
    y2 = list(int(i) for i in t['released'][-10:])
    y3 = list(int(i) for i in t['death'][-10:])

    maxY = int(max(y1+y2+y3)*11/10)

    fig, ax1 = plt.subplots()
    plt.xticks(rotation=45)

    ax1.set_ylim(0, maxY)

    line1 = ax1.plot(x, y1, c='r', label="신규확진")
    ax1.scatter(x, y1, c='r', s=10)
    line2 = ax1.plot(x, y2, c='g', label="격리해제")
    ax1.scatter(x, y2, c='g', s=10)
    line3 = ax1.plot(x, y3, c='grey', label="사망")
    ax1.scatter(x, y3, c='grey', s=10)

    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%m-%d"))

    lines = line1 + line2 + line3
    plt.legend(lines, [l.get_label() for l in lines], loc=2)

    for x_, y_ in zip(x, y1):
        label = "{0}".format(y_)

        ax1.annotate(label,
                     (x_, y_),
                     textcoords="offset points",
                     xytext=(0, 3),
                     ha='right')

    for x_, y_ in zip(x, y2):
        label = "{0}".format(y_)

        ax1.annotate(label,
                     (x_, y_),
                     textcoords="offset points",
                     xytext=(0, 3),
                     ha='right')

    for x_, y_ in zip(x, y3):
        if y_ == 0:
            continue

        label = "{0}".format(y_)

        ax1.annotate(label,
                     (x_, y_),
                     textcoords="offset points",
                     xytext=(0, 3),
                     ha='right')
    plt.savefig("./botdata/graph")

def setup(bot: CovidBot):
    bot.add_cog(Admin(bot))
