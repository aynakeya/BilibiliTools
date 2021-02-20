# from sources.bilibili.biliAudio import biliAudio,biliAudioList
# from sources.bilibili.biliVideo import biliVideo,biliBangumi
# from sources.bilibili.biliLive import biliLive
#
# models = {biliAudio.name:biliAudio,
#           biliAudioList.name:biliAudioList,
#           biliVideo.name:biliVideo,
#           biliVideoList.name:biliVideoList,
#           biliBangumi.name:biliBangumi,
#           biliLive.name:biliLive}
#
# def modelSelector(url):
#     for m in models.values():
#         if m.applicable(url):
#             return m
#     return None