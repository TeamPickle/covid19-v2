from discord.ext.commands import Cog, Context, command
from bot import CovidBot
from enum import Enum
import utils
import aiohttp, re, json, sqlite3, datetime, random
import js2py


class MapType(Enum):
    SATELLITE = "satellite"
    TERRAIN = "terrain"
    BASIC = "basic"


class Map(Cog):
    def __init__(self, bot: CovidBot):
        self.bot = bot
        self.logger = bot.get_logger(self)
        self.conn = sqlite3.connect("./maps/data.db")
        self.mapver = "00000"


        self.conn.execute("""CREATE TABLE IF NOT EXISTS "main"."position" (
            "tag"	TEXT NOT NULL,
            "date"	INTEGER NOT NULL,
            "date_text"	TEXT,
            "address"	TEXT NOT NULL,
            "address_name"	TEXT NOT NULL,
            "lat"	REAL NOT NULL,
            "long"	REAL NOT NULL,
            "profile"	TEXT NOT NULL,
            "solo"	INTEGER NOT NULL,
            "status"	TEXT,
            "name"	TEXT,
            "full"	TEXT,
            "memo"	TEXT,
            "num"	INTEGER
        )""")
        self.conn.commit()

        self.logger.info("initialized")
    
    @command(aliases=["지도"])
    async def map(self, ctx: Context, *args):
        await ctx.send(str(self.bot.latency * 1000 // 1) + "ms")
    
    @command(name="genmap")
    @utils.checkadmin()
    async def genmap(self, ctx: Context):
        async with aiohttp.ClientSession() as session:
            async with session.get("https://coronamap.site/javascripts/ndata.js") as r:
                data = await r.text('utf-8')
        position = js2py.eval_js(data)

        self.conn.execute("""DELETE FROM "main"."position" """)

        for bi in position:
            tag = bi["tag"] if "tag" in bi else ""
            if "month" in bi and "day" in bi:
                date = datetime.date(
                    2020, int(bi["month"]), int(bi["day"])).toordinal()
            else:
                date = ""
            date_text = bi["date"] if "date" in bi else ""
            address = bi["address"] if "address" in bi else ""
            address_name = bi["address_name"] if "address_name" in bi else ""
            lat, lng = map(float, bi["latlng"].split(",")[:2])
            profile = bi["profile"] if "profile" in bi else "-"
            if "solo" in bi:
                if bi["solo"]:
                    solo = 1
                else:
                    solo = 0
            else:
                solo = None
            status = bi["status"] if "status" in bi else "-"
            name = bi["name"] if "name" in bi else ""
            full = bi["full"] if "full" in bi else ""
            if "memo" in bi:
                memo = bi["memo"]
                memo = re.search(r"\d+명", memo).group()
            else:
                memo = None
            num = bi["num"] if "num" in bi else -1

            self.conn.execute(
                """INSERT INTO "main"."position"("tag","date","date_text","address","address_name","lat","long","profile","solo","status","name","full","memo","num") VALUES ('{}',{},'{}','{}','{}',{},{},'{}',{},'{}','{}','{}','{}',{})"""
                .format(tag, date, date_text, address.replace("'", "''"), address_name, lat, lng, profile, solo, status,
                        name, full, memo, num))
        self.conn.commit()

        self.mapver = str(random.randint(10000, 99999))
        await ctx.send("DB saved. mapver : "+self.mapver)



def deg2num(lat_deg, lon_deg, zoom, offset=None):
    if not 0 <= zoom <= 21:
        raise ValueError(
            "zoom has to be greater than or equal to 0 and less than or equal to 21")
    if offset:
        xtile, ytile = deg2num(lat_deg, lon_deg, zoom)
        floatX = (xtile - int(xtile) + offset) * image_size[0]
        floatY = (ytile - int(ytile) + offset) * image_size[1]

        return (int(xtile), int(ytile), int(floatX), int(floatY))
    else:
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = (lon_deg + 180.0) / 360.0 * n
        ytile = (1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n

        return (xtile, ytile)


def getZoomByBoundary(boundary, side):
    if type(boundary) == dict:  # when search address
        minX, minY, maxX, maxY = map(float, boundary.values())
    else:  # when search place
        minX, minY, maxX, maxY = map(float, boundary)
    for zoom in range(21, 5, -1):
        left, top = deg2num(minY, minX, zoom)
        right, bottom = deg2num(maxY, maxX, zoom)
        if right - left < side - 1 and bottom - top < side - 1:
            return ((minX + maxX) / 2, (minY + maxY) / 2, zoom)


async def getMap(zoom, x, y, dx, dy, mapType):
    bigbig = None

    async with aiohttp.ClientSession() as session:
        for y1 in range(y, y + dy):
            big = None
            for x1 in range(x, x + dx):
                async with session.get(f"https://map.pstatic.net/nrb/styles/{mapType.value}/1592557809/{zoom}/{x1}/{y1}.png?mt=bg.ol.lko") as res:
                    # res = requests.get("https://map.pstatic.net/nrb/styles/{type}/1588758928/{zoom}/{x}/{y}.png?mt=bg.ol.lko".format(
                    #     type=mapType.value, zoom=zoom, x=x1, y=y1), stream=True).raw
                    image = np.asarray(bytearray(await res.read()), dtype='uint8')
                    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

                    # cv2.putText(image, "{x}, {y}".format(x=x1, y=y1), (0, image_size[1] - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
                    try:
                        # big = np.concatenate((big, np.zeros((image_size[0], 1, 3), dtype='uint8')), axis=1)
                        big = np.concatenate((big, image), axis=1)
                    except ValueError:
                        big = image
            try:
                # bigbig = np.concatenate((bigbig, np.zeros((1, big.shape[1], 3), dtype='uint8')), axis=0)
                bigbig = np.concatenate((bigbig, big), axis=0)
            except ValueError:
                bigbig = big

        return bigbig


def drawMapByDeg(lat, lon, circles, zoom = 19, offset = 2, mapType = MapType.BASIC):
    zoom = int(zoom)
    offset = int(offset)
    num = deg2num(lat, lon, zoom, offset)
    img = getMap(zoom, num[0] - offset, num[1] - offset, offset * 2, offset * 2, mapType)
    for circle in circles:
        cv2.circle(img, (num[2], num[3]), 10, (0, 255, 0), -10)

    name = "./maps/" + "%032x" % random.getrandbits(128) + ".jpg"
    cv2.imwrite(name, img)
    return name


def setup(bot: CovidBot):
    bot.add_cog(Map(bot))
