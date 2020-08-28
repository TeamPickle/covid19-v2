from discord import Embed, Forbidden
from discord.ext.commands import Cog, Context, command
from bot import CovidBot
import utils

_MAIN_COMMAND = "📊 **{prefix}현황 [시/도] [시/군/구]**\n" \
                "지역을 입력하지 않으면 전국 현황을 불러옵니다.\n" \
                "시/도만 입력하신 경우 해당 시/도의 현황을 불러옵니다. ``예시: {prefix}현황 서울``\n" \
                "시/군/구까지 입력하신 경우 해당 지역의 현황을 불러옵니다. ``예시: {prefix}현황 서울 중구``\n\n" \
                "" \
                "🚩 **{prefix}현황 [국가]**\n" \
                "해당 국가의 현황을 불러옵니다. ``예시: {prefix}현황 미국``\n\n" \
                "" \
                "🌏 **{prefix}현황 세계**\n" \
                "전 세계 국가의 현황을 불러옵니다.\n\n"
                # "" \
                # ":map: **{prefix}지도 [지역]**\n" \
                # "해당 지역의 확진자 방문 장소를 지도로 보여줍니다.\n\n" \
                # "" \
                # ":mask: **{prefix}마스크 [지역]**\n" \
                # "해당 지역의 마스크 판매처 및 수량 정보를 불러옵니다. ``예시: {prefix}마스크 세종대로 110``"
_SERVER_COMMAND = "``{prefix}뉴스 [키워드]`` ``{prefix}병원 [시/도] [시/군/구]`` ``{prefix}재난문자 [시/도]`` ``{prefix}그래픽`` ``{prefix}중요뉴스 ㅇ`` ``{prefix}방해금지 ㅇ``"
_DM_COMMAND = "``{prefix}병원 [시/도] [시/군/구]`` ``{prefix}재난문자 [시/도]`` ``{prefix}그래픽``"

_SERVER_TITLE = "코로나19 알림봇 - 🌏서버용 도움말"
_DM_TITLE = "코로나19 알림봇 - 👤개인채팅용 도움말"

_GLOBAL_SETTING = "**{prefix}위치설정 [시/도] [시/군/구]**\n" \
                "내 위치를 등록합니다. 등록 후에는 명령어에 지역을 입력하지 않아도 등록한 위치의 정보를 불러옵니다.\n\n"
_SERVER_SETTING = "**{prefix}채널설정 #채널명**\n" \
                "뉴스를 전송하는 채널을 설정합니다.\n\n" \
                "**{prefix}접두사설정 [접두사]**\n" \
                "해당 서버의 명령어 접두사를 변경합니다.\n\n" \
                "**!접두사초기화**\n명령어 접두사를 !로 초기화합니다.\n\n"
_DM_SETTING = "**{prefix}현황알림 ㅇ**\n" \
                "이 옵션을 설정하면 현황 변경 시 개인 채팅으로 알려줍니다. ``{prefix}현황알림 ㄴ``을 입력하여 해제합니다.\n\n"

class Help(Cog):
    def __init__(self, bot: CovidBot):
        self.bot = bot
        self.logger = bot.get_logger(self)

        self.logger.info("initialized")
    
    @command(aliases=["도움", "도움말"])
    async def help(self, ctx: Context, *args):
        if len(args) == 0:
            await self.__fullHelp(ctx, *args)
        else:
            await self.__detailHelp(ctx, *args)
    
    async def __fullHelp(self, ctx: Context, *args):
        mode = utils.get_mode(ctx)

        settings = _GLOBAL_SETTING
        if mode == utils.Mode.SERVER:
            title = _SERVER_TITLE
            subCommand = _SERVER_COMMAND
            settings += _SERVER_SETTING
        elif mode == utils.Mode.DM:
            title = _DM_TITLE
            subCommand = _DM_COMMAND
            settings += _DM_SETTING
            
        embed = Embed(
            title=title.format(prefix=ctx.prefix),
            description="코로나19와 관련된 국내외 소식과 관련 정보를 전해드립니다.",
            color=0x0077aa
        )

        embed.add_field(
            name="주 명령어",
            value=_MAIN_COMMAND.format(prefix=ctx.prefix),
            inline=False
        )

        embed.add_field(
            name="설정 및 옵션",
            value=settings.format(prefix=ctx.prefix),
            inline=False
        )

        embed.add_field(
            name="부가 명령어({prefix}도움 [명령어이름]으로 확인가능)".format(prefix=ctx.prefix),
            value=subCommand.format(prefix=ctx.prefix),
            inline=False
        )

        embed.add_field(
            name="봇 초대",
            value="http://covid19bot.tpk.kr"
        )
        embed.add_field(
            name="버그 신고",
            value="http://forum.tpk.kr"
        )

        try:
            await ctx.author.send(embed=embed)
            if mode == utils.Mode.SERVER:
                await ctx.send("명령어 리스트를 DM으로 전송했습니다.")
        except Forbidden:
            await ctx.send(embed=embed)

    async def __detailHelp(self, ctx: Context, *args):
        title = f"{ctx.prefix} {args[0]} "
        if args[0] == "병원":
            title += "[시/도] [시/군/구]"
            desc = "해당 지역 내 선별진료소 목록을 불러옵니다.\n" \
                "예시: ``{prefix}병원 서울특별시 중구``"
        elif args[0] == "재난문자":
            title = "[시/도]"
            desc = "해당 지역에서 발송된 재난문자를 조회할 수 있습니다.\n" \
                "예시: ``{prefix}재난문자 서울``"
        elif args[0] == "그래픽":
            desc = "지역별 현황을 시각화하여 보여줍니다.\n해당 이미지는 공유가능합니다."
        elif args[0] == "뉴스":
            title += "[키워드]"
            desc = "봇이 전송한 뉴스 중 키워드가 포함된 뉴스를 가져옵니다.\n" \
                "해당 명령어는 서버 내에서만 이용가능합니다.\n" \
                "예시: ``{prefix}뉴스 확진``"
        elif args[0] == "중요뉴스":
            title += "ㅇ"
            desc = "중요뉴스만 받기 옵션을 설정합니다.\n" \
                "이 옵션을 설정하면 주요 뉴스만 서버에 전달됩니다.\n``" \
                "{prefix}중요뉴스 ㄴ``을 입력해 옵션을 해제할 수 있습니다.\n" \
                "이 명령어는 해당 서버의 관리자만 이용가능합니다."
        elif args[0] == "방해금지":
            title += "ㅇ"
            desc = "방해금지 모드 옵션을 설정합니다.\n" \
                "이 옵션을 설정하면 심야 시간(22:00~7:00)에 뉴스가 서버에 전달되지 않습니다.\n``" \
                "{prefix}방해금지 ㄴ``을 입력해 옵션을 해제할 수 있습니다.\n" \
                "이 명령어는 해당 서버의 관리자만 이용가능합니다."
        elif args[0] == "현황알림":
            title += "ㅇ"
            desc = "현황알림 옵션을 설정합니다.\n" \
                "이 옵션을 설정하면 현황 변경 시 개인 채팅으로 알려줍니다.\n``" \
                "{prefix}현황알림 ㄴ``을 입력해 옵션을 해제할 수 있습니다.\n" \
                "이 명령어는 개인 채널에서만 사용하실 수 있습니다."
        elif args[0] == "현황":
            title += "(시/도) (시/군/구) | (국가) | 세계"
            desc = "``{prefix}현황``만 입력하면 전국 현황을 불러옵니다.\n" \
                "``{prefix}현황 [시/도]``를 입력하면 해당 시/도의 현황을 불러옵니다.\n" \
                "``{prefix}현황 [시/도] [시/군/구]``를 입력하면 해당 지역의 현황을 불러옵니다.\n" \
                "``{prefix}현황 [국가]``를 입력하면 해당 국가의 현황을 불러옵니다.\n" \
                "``{prefix}현황 세계``를 입력하면 전 세계 국가의 현황을 불러옵니다.\n\n" \
                "예시: ``{prefix}현황`` ``{prefix}현황 서울`` ``{prefix}현황 서울 중구`` ``{prefix}현황 중국`` ``{prefix}현황 세계``"
        elif args[0] == "지도":
           title += "[지역]"
           desc = "해당 지역 내 확진자 방문 장소를 지도로 보여줍니다.\n" \
               "지역 입력 형식은 자유로우며, 대한민국 내 지역만 조회 가능합니다.\n" \
                "예시: ``{prefix}지도 서울 중구 명동`` ``{prefix}지도 세종대로``"
        # elif args[0] == "마스크":
        #    title += "[지역]"
        #    desc = "해당 지역 __주변__ 마스크 판매처 및 수량 정보를 지도로 보여줍니다.\n" \
        #        "지역 입력 형식은 자유로우며, 대한민국 내 지역만 조회 가능합니다.\n" \
        #        "좁은 범위로 검색해야 더 정확한 결과를 얻을 수 있습니다.\n" \
        #        "예시: ``{prefix}마스크 세종대로 110`` ``{prefix}마스크 태평로1가 13``"
        elif args[0] == "위치설정":
            title += "[시/도] [시/군/구]"
            desc = "내 위치를 등록합니다.\n" \
                "등록 후에는 ``{prefix}병원`` ``{prefix}재난문자`` 등의 명령어에 지역을 입력하지 않아도 해당 지역의 정보를 불러옵니다.\n" \
                "예시: ``{prefix}위치설정 서울 중구``"
        elif args[0] == "채널설정":
            title += "#채널명"
            desc = "서버에 뉴스를 전송하는 채널을 설정합니다.\n" \
                "이 명령어는 해당 서버의 관리자만 이용가능합니다.\n" \
                "예시: ``{prefix}채널설정 #코로나현황``"
        elif args[0] == "접두사설정":
            title += "[접두사]"
            desc = "서버 내 명령어 접두사를 변경합니다.\n" \
                "접두사는 명령어 앞에 붙여 쓰는 식별자를 의미합니다. 현재 접두사는 **{prefix}**입니다.\n" \
                "이 명령어는 해당 서버의 관리자만 이용가능합니다.\n" \
                "예시: ``{prefix}접두사설정 &`` - 이후 ``&도움`` 등과 같이 사용가능\n\n" \
                "접두사를 잊어버린 경우 ``!접두사초기화``를 이용하여 접두사를 !로 초기화할 수 있습니다."
        else:
            return
        embed = Embed(
            title =title,
            description=desc.format(prefix=ctx.prefix),
            color=0x0077bb
        )
        await ctx.send(embed=embed)

def setup(bot: CovidBot):
    bot.add_cog(Help(bot))
