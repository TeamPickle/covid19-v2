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
        self.db = bot.pickle_db
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
    @utils.userpos
    async def map(self, ctx: Context, *args):
        args = " ".join(args)
        async with aiohttp.ClientSession() as session:
            async with session.get(f"https://map.naver.com/v5/api/search?caller=pcweb&query={args}") as r:
                res = await r.json()
        await ctx.send(args + "(으)로 검색중입니다.")

        name = "./maps/"+args[0].encode('utf-8').hex()+mapver+".png"
        if os.path.isfile(name):
            await ch.send(file=discord.File(name))
            return
        
        async with ctx.typing():
            res = res["result"]
            try:
                if res["address"]:
                    if res["address"]["jibunsAddress"]:
                        jibunAddress = res["address"]["jibunsAddress"]["list"][0]
                        addressId = jibunAddress["id"]
                        boundary = jibunAddress["boundary"]
                    elif res["address"]["roadAddress"]:
                        jibunAddress = res["address"]["roadAddress"]["list"][0]
                        addressId = jibunAddress["id"]
                        boundary = jibunAddress["boundary"]
                    else:
                        boundary = None
                elif res["place"]:
                    addressId = None
                    jibunAddress = res["place"]
                    boundary = jibunAddress["boundary"]
                else:
                    boundary = None

                if boundary:
                    x, y, z = getZoomByBoundary(boundary, 5)
                    # print(boundary)

                    if type(boundary) == dict:  # when search address
                        minX, minY, maxX, maxY = map(
                            float, boundary.values())
                    else:  # when search place
                        minX, maxY, maxX, minY = map(
                            float, boundary)
                    minX -= 0.5
                    maxX += 0.5
                    minY -= 0.5
                    maxY += 0.5
                    # print(x, y, z)
                    x, y = map(int, deg2num(y, x, z))
                    # print(x, y)
                    # name = drawMapByDeg(y, x, z) # 다 꼬였다 에라이
                    img = await getMap(z, x - 2, y - 2, 5,
                                    5, MapType.BASIC)
                    for i in conn.execute(
                        'SELECT * FROM "main"."position" WHERE "lat" BETWEEN {} AND {}  AND "long" BETWEEN {} AND {};'
                            .format(minY, maxY, minX, maxX)):
                        # date = datetime.date.fromordinal(i[1])
                        # if i[2] != -1:
                        x1, y1 = deg2num(i[5], i[6], z)
                        x1 = int((x1 - x + 2) * image_size[0])
                        y1 = int((y1 - y + 2) * image_size[1])
                        date = datetime.date.fromordinal(i[1])
                        today = datetime.date.today()
                        days = (today - date).days
                        if days == 0:
                            color = (0, 0, 255)
                        elif days >= 4:
                            color = (0, 255, 0)
                        else:
                            color = (0, 255, 255)
                        # color = int(i[2])
                        # (color & 0xff, color & 0xff00, color & 0xff0000)
                        cv2.circle(img, (x1, y1), z //
                                2 + 4, (0, 0, 0), -1)
                        cv2.circle(img, (x1, y1), z //
                                2 + 3, color, -1)

                    if addressId:
                        async with aiohttp.ClientSession() as session:
                            async with session.get("https://map.naver.com/v5/api/wfs/stargate?output=geojson&targetcrs=epsg:4326&codetype=naver&request=codeToFeatures&level={}&keyword={}".format(z, addressId)) as res_1:
                                feature = await res_1.json()
                        geometry = feature["features"][0]["geometry"]
                        coordss = geometry["coordinates"]
                        if geometry["type"] == "MultiPolygon":
                            for coords in coordss:
                                codArr = None
                                for coord in coords[0]:
                                    x1, y1 = deg2num(
                                        coord[1], coord[0], z)
                                    x1 = int(
                                        (x1 - x + 2) * image_size[0])
                                    y1 = int(
                                        (y1 - y + 2) * image_size[1])
                                    try:
                                        codArr = np.append(
                                            codArr, [[x1, y1]], axis=0)
                                    except ValueError:
                                        codArr = [[x1, y1]]
                                cv2.polylines(
                                    img, [codArr], False, (255, 0, 0), 2)
                        elif geometry["type"] == "Polygon":
                            for coords in coordss:
                                codArr = None
                                for coord in coords:
                                    x1, y1 = deg2num(
                                        coord[1], coord[0], z)
                                    x1 = int(
                                        (x1 - x + 2) * image_size[0])
                                    y1 = int(
                                        (y1 - y + 2) * image_size[1])
                                    try:
                                        codArr = np.append(
                                            codArr, [[x1, y1]], axis=0)
                                    except ValueError:
                                        codArr = [[x1, y1]]
                                cv2.polylines(
                                    img, [codArr], False, (0, 0, 255), 2)

                    cv2.imwrite(name, img)
                    await ch.send(file=discord.File(name))
                else:
                    await ch.send("검색결과가 없습니다. 좀더 넓은 범위로 검색해주세요.")
            except KeyError:
                await ch.send("해당 지역을 찾을 수 없습니다.")


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
