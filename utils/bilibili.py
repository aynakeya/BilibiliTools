import os
import re
import time

import qrcode

from config import Config
from utils.vhttp import httpGet, httpPost


class videoIdConvertor():
    videoUrl = "https://www.bilibili.com/video/%s"
    patternAv = r"av[0-9]+"
    patternBv = r"BV[0-9,A-Z,a-z]+"
    table = 'fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF'
    tr = dict(("fZodR9XQDSUm21yCkr6zBqiveYah8bt4xsWpHnJE7jL5VG3guMTKNPAwcF"[i], i) for i in range(58))
    s = [11, 10, 3, 8, 4, 6]
    xor = 177451812
    add = 8728348608

    @classmethod
    def bv2av(cls, x):
        r = 0
        for i in range(6):
            r += cls.tr[x[cls.s[i]]] * 58 ** i
        return (r - cls.add) ^ cls.xor

    @classmethod
    def av2bv(cls, x):
        x = (int(x) ^ cls.xor) + cls.add
        r = list('BV1  4 1 7  ')
        for i in range(6):
            r[cls.s[i]] = cls.table[x // 58 ** i % 58]
        return ''.join(r)

    @classmethod
    def urlConvert(cls, url):
        if re.search(cls.patternBv, url):
            return cls.videoUrl % ("av%s" % cls.bv2av(re.search(cls.patternBv, url).group()))
        if re.search(cls.patternAv, url):
            return cls.videoUrl % cls.av2bv(int(re.search(cls.patternAv, url).group()[2::]))
        return ""

class QrLogin():
    infoApi = "https://account.bilibili.com/home/userInfo"
    qrApi = "https://passport.bilibili.com/qrcode/getLoginUrl"
    checkQrApi = "https://passport.bilibili.com/qrcode/getLoginInfo"

    def __init__(self,invert=False,console=False):
        self.invert = invert
        self.console = console
        self.oauthKey = ""
        self.urldata = ""

    @staticmethod
    def manuallylogin():
        ql = QrLogin.newlogin()
        print("getting qrcode")
        ql.getQrcode()
        print("Please scan qrcode using your application")
        if ql.getResult():
            print("login success, you Sessdata is %s" % ql.getSessdata())
            Config.getCookie("bilibili")["SESSDATA"] = ql.getSessdata()
            if input("write to the config? y/n ") == "y":
                Config.saveCookie()
        else:
            print("fail, please try again")

    @classmethod
    def newlogin(cls):
        a= input("invert color? y/n ") == "y"
        b = input("Console output? y/n ") == "y"
        return cls(a,b)

    @classmethod
    def isLogin(cls):
        return Config.getCookie("bilibili").get("SESSDATA") != None
        # resp = httpGet(cls.infoApi,cookies=Config.commonCookies)
        # try:
        #     print(resp.json())
        #     return resp.json()["code"] == 0
        # except:
        #     return False

    def getQrcode(self):
        data = httpGet(self.qrApi).json()

        qrurl = data["data"]["url"]
        self.oauthKey = data["data"]["oauthKey"]
        qc = qrcode.QRCode()
        qc.add_data(qrurl)
        if self.console:
            qc.print_ascii(invert=self.invert)
        else:
            qc.make_image().save("./qrcode.png")
            os.system("qrcode.png")

    def getResult(self,interval=1):
        data = httpPost(self.checkQrApi,data={'oauthKey':self.oauthKey,'gourl': 'https://passport.bilibili.com/account/security'})
        if data == None:
            return False
        while not data.json()["status"]:
            data = httpPost(self.checkQrApi,
                            data={'oauthKey': self.oauthKey, 'gourl': 'https://passport.bilibili.com/account/security'})
            if data.json()['data'] == -2:
                print('二维码已过期')
                return False
            time.sleep(interval)
        self.urldata = data.json()["data"]["url"]
        return True
    def getSessdata(self):
        pattern = r"SESSDATA=(.*?)&"
        return "" if re.search(pattern,self.urldata) == None else re.search(pattern,self.urldata).group()[9:-1:]

    def isValid(self):
        return self.oauthKey != ""


def danmuass(path):
    pass