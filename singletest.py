from config import Config
from downloaders.aria2 import ariaDownloader
from sources.base import MediaSource
dl = ariaDownloader()
m = MediaSource("https://youku.cdn7-okzy.com/20200129/16898_4aa9a693/1000k/hls/index.m3u8",
            {},"index.m3u8")

m.download(dl,Config.saveroute)