import discord
from bot import CovidBot
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime

async def makeGraph(t, bot: CovidBot):
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

    await bot.change_presence(status=discord.Status.do_not_disturb, activity=discord.Game(
        name=f"!도움 | 신규확진 {y1[-1]}명 | shard0 {len(bot.guilds)}서버"))