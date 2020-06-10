from config import Config
from utils import filenameparser,httpGet
import os

class requestsDownloader():
    name = "requests"

    def __init__(self):
        pass

    def download(self, url, route, filename,**kwargs):
        fn = filenameparser(filename)
        raw_data = httpGet(url, **kwargs)
        if raw_data == None:
            return False
        path = os.path.join(route, fn)
        if not os.path.exists(route):
            os.mkdir(route)
        with open(path,"wb+") as f:
            f.write(raw_data.content)
        return True
