from discord import Message, File
from discord.ext.commands import Cog, Context, command
from bot import CovidBot
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager, rc
import aiohttp, re, datetime, os
import utils


class Admin(Cog):
    def __init__(self, bot: CovidBot):
        self.bot = bot
        self.db = bot.pickle_db
        self.logger = bot.get_logger(self)

        font_manager.get_fontconfig_fonts()
        font_name = font_manager.FontProperties(fname="./malgunbd.TTF").get_name()
        rc('font', family=font_name)

        if not os.path.exists("botdata"):
            os.mkdir("botdata")

        self.logger.info("initialized")

    
    @command(name="send", aliases=["전송"])
    async def send(self, ctx: Context):
        await ctx.send(str(self.bot.latency * 1000 // 1) + "ms")
    
    @command(name="graph")
    @utils.checkadmin()
    async def graph(self, ctx: Context):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://coronaboard.kr/') as r:
                res = await r.text('utf-8')
        t = eval(re.findall(
            'Global":{"KR":(.+?),"global"', res)[0])

        await makeGraph(t)
        graphmsg: Message = await ctx.send(file=File("./botdata/graph.png"))
        self.db["covid19"]["graphs"].insert_one({
            "_id": graphmsg.attachments[0].url,
            "createdAt": datetime.datetime.now().utcnow()
        })


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
