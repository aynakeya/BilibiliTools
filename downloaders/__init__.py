from .aria2 import ariaDownloader
from .requests import requestsDownloader

downloaders = {ariaDownloader.name:ariaDownloader,
               requestsDownloader.name:requestsDownloader}
