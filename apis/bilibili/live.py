from apis import CommonRequestWrapper
from urllib import parse

class FORMAT:
    HLS = ("hls","h5")
    FLV = ("flv","web")

    values = [HLS,FLV]

    @staticmethod
    def format(fmt):
        return fmt[0]

    @staticmethod
    def platform(fmt):
        return fmt[1]

    @staticmethod
    def getPlatformByFormat(fmt):
        for v in FORMAT.values:
            if fmt == FORMAT.format(v):
                return FORMAT.platform(v)
        return FORMAT.platform(FORMAT.HLS)

class API:

    @staticmethod
    def info_api(id):
        return "https://api.live.bilibili.com/room/v1/Room/room_init?id={}".format(id)

    @staticmethod
    def playurl_api(real_room_id,platform):
        params = {
            'cid': real_room_id,
            'qn': 10000,
            'platform': platform,
            'https_url_req': 1,
            'ptype': 16
        }
        return "https://api.live.bilibili.com/xlive/web-room/v1/playUrl/playUrl?{}".format(parse.urlencode(params))


@CommonRequestWrapper
def getLiveInfo(room_id:str):
    """
    get live room info including real room id

    :param room_id: the room id display in the url or web
    :return:
    """
    return ("get",
            API.info_api(room_id))

@CommonRequestWrapper
def getRealUrlByPlatform(real_room_id,platform):
    """

    :param real_room_id: the real room id
    :param platform: see in bilibili.live.FORMAT
    :return:
    """
    return ("get",
            API.playurl_api(real_room_id,platform))

@CommonRequestWrapper
def getRealUrlByFormat(real_room_id,format):
    """

    :param real_room_id: the real room id
    :param platform: see in bilibili.live.FORMAT
    :return:
    """
    return ("get",
            API.playurl_api(real_room_id,FORMAT.getPlatformByFormat(format)))