from discord import File
from discord.ext.commands import Cog, Context, command
from bot import CovidBot
import aiohttp
import re
from PIL import Image, ImageFont, ImageDraw


class Graphic(Cog):
    t_prev = {}
    def __init__(self, bot: CovidBot):
        self.bot = bot
        self.logger = bot.get_logger(self)

        self.logger.info("initialized")
    
    @command(aliases=["그래픽"])
    async def graphic(self, ctx: Context):
        async with aiohttp.ClientSession() as session:
            async with session.get('https://coronaboard.kr/') as r:
                res = await r.text('utf-8')
        t = eval(re.findall('"statByKrLocation":(.+?}]),', res)[0])
        if t != self.t_prev:
            self.t_prev = t
            k = {}
            cnt = 0
            for item in t:
                cnt += item['confirmed']
                k[item['region']] = item['confirmed']

            img = Image.new("RGBA", (1665, 1125), (30, 30, 30))
            draw = ImageDraw.Draw(img)
            img3 = Image.open("./local/bg.png")
            img3.thumbnail((1665, 1125))
            img.paste(img3, (0, 0))
            x = [345, 276, 244, 248, 396, 413, 293, 331,
                    143, 389, 413, 489, 570, 662, 633, 463, 610]
            y = [342, 353, 234, 454, 519, 562, 618, 776,
                    739, 172, 426, 366, 648, 700, 755, 664, 898]
            loc = ['서울', '인천', '경기', '충남', '세종', '대전', '전북', '광주',
                    '전남', '강원', '충북', '경북', '대구', '울산', '부산', '경남', '제주']

            for i in range(17):
                img = alpha(k[loc[i]], cnt, x[i], y[i], i + 1, img)

            chart = Image.open("./local/k.png").convert("RGBA")
            img.paste(chart, (213, 10), chart)
            font = ImageFont.truetype("malgunbd.TTF", 40)

            x2 = [20, 20, 20, 20, 20, 20, 20, 20, 20, 1390,
                    1390, 1390, 1390, 1390, 1390, 1390, 1390]
            y2 = [23, 200, 300, 410, 520, 675, 775, 915,
                    1000, 167, 253, 423, 513, 685, 775, 933, 1023]
            for i in range(17):
                draw.text((x2[i], y2[i]), str(k[loc[i]]) + "(" + str(round(k[loc[i]] / cnt * 100, 1)) + "%)", (0, 0, 0),
                            font=font)

            img.save('./local/final.png')
            await ctx.send(file=File('./local/final.png'))
        else:
            await ctx.send(file=File('./local/final.png'))


def alpha(k, cnt, x, y, i, img):
    x += 358
    y += 44
    if k / cnt * 100 > 20:
        f2 = Image.open('./local/'+str(i)+'.png').convert('RGBA')
        img.paste(f2, (x, y), mask=f2)
    elif k / cnt * 100 > 1.5:
        f2 = Image.open('./local/h'+str(i)+'.png').convert('RGBA')
        img.paste(f2, (x, y), mask=f2)
    elif k / cnt * 100 > 0.5:
        f2 = Image.open('./local/hh'+str(i)+'.png').convert('RGBA')
        img.paste(f2, (x, y), mask=f2)
    else:
        f2 = Image.open('./local/hhh'+str(i)+'.png').convert('RGBA')
        img.paste(f2, (x, y), mask=f2)
    return img


def setup(bot: CovidBot):
    bot.add_cog(Graphic(bot))
