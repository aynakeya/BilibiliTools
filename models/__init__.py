from .biliAudio import biliAudio,biliAudioList
from .biliVideo import biliVideo,biliVideoList,biliBangumi

models = {biliAudio.name:biliAudio,
          biliAudioList.name:biliAudioList,
          biliVideo.name:biliVideo,
          biliVideoList.name:biliVideoList,
          biliBangumi.name:biliBangumi}