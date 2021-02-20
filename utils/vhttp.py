import requests

from config import Config


def httpGet(url, maxReconn=5,proxy=Config.useProxy, **kwargs):
    trial = 0
    if proxy:
        kwargs["proxies"] = Config.proxies
    while trial < maxReconn:
        try:
            return requests.get(url, timeout=5, **kwargs)
        except:
            trial += 1
            continue
    return None

def httpPost(url, maxReconn=5,proxy=Config.useProxy,**kwargs):
    trial = 0
    if proxy:
        kwargs["proxies"] = Config.proxies
    while trial < maxReconn:
        try:
            return requests.post(url, timeout=5, **kwargs)
        except:
            trial += 1
            continue
    return None
