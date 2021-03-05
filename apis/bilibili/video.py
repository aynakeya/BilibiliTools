from apis import CommonRequestWrapper
from config import Config


class QUALITY:
    P4k = (120, "FLV", "超清 4K", True)
    P1080F60 = (116, "FLV", "高清 1080P60", True)
    P1080PLUS = (112, "FLV", "高清 1080P+", True)
    P1080 = (80, "FLV", "高清 1080P", True)
    P720F60 = (74, "FLV", "高清 720P", True)
    P720 = (64, "FLV", "高清 720P", True)
    P720MP4 = (48, "MP4", "高清 720P (MP4)", True)
    P480 = (32, "FLV", "清晰 480P", False)
    P360 = (16, "FLV", "流畅 360P", False)

    values = [P4k, P1080F60, P1080PLUS, P1080,
              P720F60, P720, P720MP4,
              P480, P360]

    @staticmethod
    def id(quality):
        return quality[0]

    @staticmethod
    def format(quality):
        return quality[1]

    @staticmethod
    def description(quality):
        return quality[2]

    @staticmethod
    def cookie(quality):
        return quality[3]


class API:
    cookies = Config.getCookie("bilibili")

    @staticmethod
    def headers():
        h = Config.commonHeaders.copy()
        h.update({"referer": "https://www.bilibili.com"})
        return h

    @staticmethod
    def detail_api(bvid):
        return "https://api.bilibili.com/x/web-interface/view/detail?" \
               "bvid={bvid}&aid=&jsonp=jsonp".format(bvid=bvid)

    @staticmethod
    def pages_api(bvid):
        return "https://api.bilibili.com/x/player/pagelist?bvid={bvid}".format(bvid=bvid)

    @staticmethod
    def playurl_api(bvid, cid, quality):
        return "https://api.bilibili.com/x/player/playurl?type=&otype=json&fourk=1&" \
               "avid=&bvid={bvid}&cid={cid}&qn={quality}".format(bvid=bvid,
                                                                 cid=cid,
                                                                 quality=quality)

    @staticmethod
    def bangumi_url(ep_id):
        return "https://www.bilibili.com/bangumi/play/{ep_id}".format(ep_id=ep_id)

    @staticmethod
    def bangumi_playurl_api(bvid, cid, quality):
        return "https://api.bilibili.com/pgc/player/web/playurl?type=&otype=json&fourk=1&" \
               "avid=&bvid={bvid}&cid={cid}&qn={quality}".format(bvid=bvid,
                                                                 cid=cid,
                                                                 quality=quality)


    @staticmethod
    def danmu_api(cid):
        return "http://comment.bilibili.com/{cid}.xml".format(cid=cid)


@CommonRequestWrapper
def getVideoInfo(bvid: str):
    """
    return video ifo

    :param bvid: bilibili bvid
    :return: bytes
    """
    return ("get",
            API.detail_api(bvid),
            {"headers": API.headers()}
            )


@CommonRequestWrapper
def getVideoCid(bvid: str):
    """
    return video pages including page name and cid

    :param bvid: bilibili bvid
    :return: bytes
    """
    return ("get",
            API.pages_api(bvid),
            {"headers": API.headers(),
             "cookies": API.cookies}
            )


@CommonRequestWrapper
def getPlayUrl(bvid: str, cid: str, quality: int = QUALITY.id(QUALITY.P1080F60)):
    """
    return video real url by bvid and cid

    :param bvid: bilibili bvid
    :return: bytes
    """
    return ("get",
            API.playurl_api(bvid, cid, quality),
            {"headers": API.headers(),
             "cookies": API.cookies}
            )


@CommonRequestWrapper
def getBangumiInfo(ep_id:str):
    """
    get bangumi info by ep id or ss id epxxx ssxxxx

    :param ep_id: bilibili ep_id
    :return: bytes
    """
    return ("get",
            API.bangumi_url(ep_id),
            {"headers": API.headers(),
             "cookies": API.cookies}
            )


@CommonRequestWrapper
def getBangumiPlayUrl(bvid: str, cid: str, quality: int = QUALITY.id(QUALITY.P1080F60)):
    """
    return video real url by bvid and cid

    :param bvid: bilibili bvid
    :return: bytes
    """
    return ("get",
            API.bangumi_playurl_api(bvid, cid, quality),
            {"headers": API.headers(),
             "cookies": API.cookies}
            )



# videoUrl = "https://www.bilibili.com/video/av%s"
# baseUrl = "https://www.bilibili.com/video/%s"
# pagesApi = "https://www.bilibili.com/widget/getPageList?aid=%s"
# pagesApi = "https://api.bilibili.com/x/player/pagelist?bvid=%s"
# detailApi = "https://api.bilibili.com/x/web-interface/view/detail?bvid=%s&aid=&jsonp=jsonp"
# playurlApi = "https://api.bilibili.com/x/player/playurl?avid=&bvid=%s&cid=%s&qn=%s&type=&otype=json&fourk=1"
# dmApi = "http://comment.bilibili.com/%s.xml"
