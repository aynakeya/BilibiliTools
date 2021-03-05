from apis import CommonRequestWrapper, RegExpResponseContainer

class QUALITY:
    HIGH = ("2","320k","高品质")
    MEDIAN = ("1","196k","标准")
    NORMAL = ("0","128k","流畅")

    values = [HIGH,MEDIAN,NORMAL]

    @staticmethod
    def id(quality):
        return quality[0]

    @staticmethod
    def bitrate(quality):
        return quality[1]

    @staticmethod
    def description(quality):
        return quality[2]

class API:
    headers = {"user-agent": "BilibiliClient/2.33.3",
               'Accept': "*/*",
               'Connection': "keep-alive"}

    @staticmethod
    def info_api(song_id):
        return "https://www.bilibili.com/audio/music-service-c/web/song/info?sid={song_id}".format(song_id = song_id)

    @staticmethod
    def file_api(song_id,quality):
        return "http://api.bilibili.com/audio/music-service-c/url?" \
               "mid=8047632&mobi_app=iphone&platform=ios&privilege=2" \
               "&quality={quality}&songid={song_id}".format(song_id = song_id,
                                              quality = quality)

    @staticmethod
    def search_api(keyword,page,pagesize):
        return "https://api.bilibili.com/audio/music-service-c/s?search_type=music&" \
               "keyword={keyword}&page={page}&pagesize={pagesize}".format(keyword=keyword,
                                                                        page=page,
                                                                        pagesize= pagesize)


@CommonRequestWrapper
def getAudioInfo(song_id:str):
    """
    get audio info

    :param song_id:
    :return:
    """
    return ("get",
            API.info_api(song_id),
            {"headers":API.headers}
            )

@CommonRequestWrapper
def getAudioFile(song_id:str,quality = QUALITY.id(QUALITY.HIGH)):
    """
    get audio file url

    :param song_id: song id
    :param quality: quality id, see bilibili.audio.QUALITY
    :return: bytes
    """
    return ("get",
            API.file_api(song_id,quality),
            {"headers": API.headers}
            )

@CommonRequestWrapper
def getSearchResult(keyword,page:int = 1,pagesize:int = 5):
    """
    get search result

    :param keyword: string keywords
    :param page: default value 1, should be integer larger or equal to 1
    :param pagesize: default value 5
    :return: bytes
    """
    return ("get",
            API.search_api(keyword,page,pagesize)
            )

# from apis import JsonResponseContainer
# container = JsonResponseContainer(getAudioFile("18439063333333",quality=2),
#                                           cdns = "data.cdns")
#
# print(container.data)