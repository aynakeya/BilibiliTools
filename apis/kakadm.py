from apis import CommonRequestWrapper, RegExpResponseContainer
from config import Config


class API:
    cookies = Config.getCookie("kakadm")

    @staticmethod
    def player_api(aid,pid):
        return "http://www.kakadm.com/anime/{aid}/{pid}/".format(aid=aid,pid=pid)

    @staticmethod
    def src_api(aid, pid):
        return "http://www.kakadm.com/e/action/player_i.php?id={aid}&pid={pid}".format(aid=aid, pid=pid)
    @staticmethod
    def real_src_api(src):
        return "http://www.kakadm.com/yun/yun.php?vid={src}".format(src=src)


@CommonRequestWrapper
def getVideoInfo(aid: str,pid:str):
    return ("get",
            API.player_api(aid,pid),
            {"cookies":API.cookies})
@CommonRequestWrapper
def getVideoUrl(aid: str,pid:str):
    return ("get",
            API.src_api(aid, pid),
            {"cookies": API.cookies})

@CommonRequestWrapper
def resolveVideoUrl(src:str):
    return ("get",
            API.real_src_api(src),
            {"cookies": API.cookies})

