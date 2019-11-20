from .biliAudio import biliAudio,biliAudioList
from .biliVideo import biliVideo,biliVideoList

models = {biliAudio.name:biliAudio,
          biliAudioList.name:biliAudioList,
          biliVideo.name:biliVideo,
          biliVideoList.name:biliVideoList}