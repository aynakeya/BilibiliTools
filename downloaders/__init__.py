from config import Config

downloaders = {}
if Config.useDownloader["requests"]:
    from .requests import requestsDownloader
    downloaders[requestsDownloader.name] = requestsDownloader


if Config.useDownloader["aria2"]:
    from .aria2 import ariaDownloader
    downloaders[ariaDownloader.name] = ariaDownloader
