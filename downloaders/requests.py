from config import Config
from downloaders import BaseDownloader
from utils import vhttp,file
import os

class requestsDownloader(BaseDownloader):
    name = "requests"

    def __init__(self):
        pass

    def download(self, url, route, filename,**kwargs):
        fn = file.parseFilename(filename)
        raw_data = vhttp.httpGet(url, **kwargs)
        if raw_data == None:
            return False
        path = os.path.join(route, fn)
        if not os.path.exists(route):
            os.mkdir(route)
        with open(path,"wb+") as f:
            f.write(raw_data.content)
        return True
