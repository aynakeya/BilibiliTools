from apis import CommonRequestWrapper, RegExpResponseContainer
from config import Config
from urllib import parse


class API:
    @staticmethod
    def player_url(id,source_id,ep_id):
        return "http://www.imomoe.ai/player/{id}-{sid}-{eid}.html".format(id=id,
                                                                          sid = source_id,
                                                                          eid=ep_id)
    @staticmethod
    def playdata_url(playdata_url):
        return parse.urljoin("http://www.imomoe.ai/",playdata_url)

    @staticmethod
    def real_src_api(src):
        return "https://api.xiaomingming.org/cloud/mp6.php?vid={src}".format(src=src)

    @staticmethod
    def search_api(keyword,page):
        return "http://www.imomoe.ai/search.asp?searchword={keyword}&page={page}"\
            .format(keyword=parse.quote(keyword, encoding="gb2312"),page=page)


@CommonRequestWrapper
def getVideoInfo(id:str,source_id:str,ep_id:str):
    return ("get",
            API.player_url(id,source_id,ep_id)
            )

@CommonRequestWrapper
def getPlaydata(playdata_url):
    return ("get",
            API.playdata_url(playdata_url)
            )
@CommonRequestWrapper
def resolveVideoUrl(src):
    return ("get",
            API.real_src_api(src)
            )
