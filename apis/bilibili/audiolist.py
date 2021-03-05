from apis import CommonRequestWrapper, SETTING


class API:

    @staticmethod
    def info_api(id,page,pagesize):
        return "https://www.bilibili.com/audio/music-service-c/web/song/of-menu?" \
               "ps={pagesize}&sid={id}&pn={page}".format(id = id,
                                                         page = page,
                                                         pagesize = pagesize)

    # @staticmethod
    # def search_api(keyword,page,pagesize):
    #     return "https://api.bilibili.com/audio/music-service-c/s?search_type=music&" \
    #            "keyword={keyword}&page={page}&pagesize={pagesize}".format(keyword=keyword,
    #                                                                     page=page,
    #                                                                     pagesize= pagesize)


@CommonRequestWrapper
def getAudioListInfo(songlist_id:str,page:int=1,pagesize:int=100):
    """
    get audiolist information

    :param songlist_id: amxxxx
    :param page: page default1
    :param pagesize: default 100
    :return:
    """
    return ("get",
            API.info_api(songlist_id,page,pagesize),
            {"headers":SETTING.common_header}
            )
