class Config:
    proxies = {}
    commonHeaders = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
    }
    commonCookies = {
                     "SESSDATA":"",
    }
    saveroute = r"D:\Download\bilidown"

    aria2rpc = "http://localhost:6800/rpc"
    #if no token provide, using None
    aria2token = None

    defaultDownloader = "requests"

    #useDownloader = ["aria2","requests"]
    useDownloader = ["requests"]

    useModules  = ["infoEditor"]

    defaultQuality = 116
