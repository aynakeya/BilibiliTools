class Config:
    proxies = {}
    commonHeaders = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0",
    }

    # 如果没有就不要填不然会报错
    SESSDATA = "fd86fe3c%2C1629279204%2Cef4b0%2A21"

    saveroute = r"D:\Download\bilidown"

    aria2rpc = "http://localhost:6800/rpc"
    # if no token provide, using None
    aria2token = None

    defaultDownloader = "aria2"

    # Available: aria2, requests
    useDownloader = {"aria2": True,
                     "requests": True}

    useModules = ["Login", "VideoIdConverter", "Info", "Download", "MPV","Wenku8"]

    defaultQuality = 120
    commonCookies = {
        "Rua":"Rua",
        "SESSDATA": SESSDATA,
    } if SESSDATA != "" else {}
