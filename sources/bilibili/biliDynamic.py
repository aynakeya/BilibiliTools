from utils.vhttp import httpGet
from config import Config


class biliDynamic:
    name = "dynamic"

    dynamicApi = "https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/dynamic_new?type_list=268435455"

    def __init__(self):
        pass

    def getByUid(self,uid):
        pass

    def getMy(self):
        pass

    def getMyNew(self,cookie=Config.getCookie("bilibili")):
        resp = httpGet(self.dynamicApi, cookies=cookie)
        if resp == None:
            return []
        resp = resp.json()
        if resp["code"] == 0 and len(resp["data"]["cards"]) > 0:
            tmp = self.current
            self.current = resp["data"]["cards"][0]["desc"]["dynamic_id"]
            return [c["desc"] for c in resp["data"]["cards"] if c["desc"]["dynamic_id"] > tmp]
        return []