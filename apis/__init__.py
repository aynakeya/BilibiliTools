from functools import wraps
from typing import List

from utils import vhttp, formats
import json,re

HTTP_CLIENT = vhttp.HttpClient()

class SETTING:
    common_header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:51.0) Gecko/20100101 Firefox/51.0"
    }

class RequestMethod:
    GET = "get"
    POST = "post"


def BaseApiWrapper(api_wrapper):
    @wraps(api_wrapper)
    def ApiWrapper(api_func):
        @wraps(api_func)
        def process(*args, **kwargs):
            retval = api_func(*args, **kwargs)
            method, url = retval[0], retval[1]
            req_kwargs = retval[2] if len(retval) >= 3 else {}
            return api_wrapper(method, url, **req_kwargs)

        return process
    return ApiWrapper


@BaseApiWrapper
def CommonRequestWrapper(method, url, **request_kwargs) -> bytes:
    if method == RequestMethod.GET:
        return HTTP_CLIENT.get(url, **request_kwargs)
    elif method == RequestMethod.POST:
        return HTTP_CLIENT.post(url, **request_kwargs)
    return b''

class RegExpResponseContainer():
    def __init__(self, content:bytes, strip:[str,List]=None, **kwargs):
        """
        :param content: the byte content of the api
        :param strip: list of str that need to be stripped
        :param kwargs: data you wants to get
        """
        self.content = content
        self.kwargs = kwargs
        self.strip = strip
        self.data = {}

        self.__process()

    def __process(self):
        text = self.__stripHTML(formats.htmlAutoDecode(self.content))
        for key,val in self.kwargs.items():
            try:
                if isinstance(val,tuple):
                    self.data[key] = val[1](re.search(val[0],text).group())
                else:
                    self.data[key] = re.search(val,text).group()
            except:
                self.data[key] = None

    def __stripHTML(self,text):
        if self.strip != None:
            if isinstance(self.strip,str):
                text = text.replace(self.strip, "")
            else:
                for s in self.strip:
                    text = text.replace(s,"")
        return text

class JsonResponseContainer():
    def __init__(self, content:bytes, path_sep=".", **kwargs):
        self.content = content
        self.kwargs = kwargs
        self.data = {}
        self.path_sep = path_sep

        self.__process()

    def __process(self):
        jdata = json.loads(self.content)
        for key,val in self.kwargs.items():
            if isinstance(val,tuple):
                self.data[key] = val[1](self.__tryFind(jdata,val[0].split(self.path_sep),0))
            else:
                self.data[key] = self.__tryFind(jdata,val.split(self.path_sep),0)

    def __tryFind(self,data,paths,now):
        if now == len(paths) - 1:
            return data[paths[now]]
        return self.__tryFind(data[paths[now]], paths, now + 1)
