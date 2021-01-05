from .biliAudio import biliAudio,biliAudioList
from .biliVideo import biliVideo,biliVideoList,biliBangumi
from .biliLive import biliLive

models = {biliAudio.name:biliAudio,
          biliAudioList.name:biliAudioList,
          biliVideo.name:biliVideo,
          biliVideoList.name:biliVideoList,
          biliBangumi.name:biliBangumi,
          biliLive.name:biliLive}

def modelSelector(url):
    for m in models.values():
        if m.applicable(url):
            return m
    return None