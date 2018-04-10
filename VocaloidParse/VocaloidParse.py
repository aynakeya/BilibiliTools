# -*- coding:utf-8 -*-

from functools import reduce

def parsetitle(title):

    def getkey(singerlist):
        return str(reduce(lambda x, y: x + y, map(lambda singer: vsingerdict[singer], singerlist)))

    def combinesingers(used, notused):
        if len(notused) < 1:
            return
        newnotused = notused.copy()
        for singer in notused:
            newused = used.copy()
            newused.append(singer)
            newnotused.remove(singer)
            vsingersdict[getkey(newused)] = "、".join(newused)
            combinesingers(newused, newnotused)


    vsingerlist = ["洛天依", "言和", "乐正绫", "心华", "星尘", "乐正龙牙","初音未来"]
    vsingerdict = {"洛天依": 2,  # 0b10
                   "乐正绫": 4,  # 0b100
                   "言和": 8,  # 0b1000
                   "心华": 16,  # 0b10000
                   "星尘": 32,  # 0b100000
                   "乐正龙牙": 64,# 0b1000000
                   "龙牙": 64,
                   "初音未来": 128,
                   "初音": 128
                   }

    album = "Vocaloid"
    vsingersdict = {"0":""}
    combinesingers([],vsingerlist)
    singerskey = 0

    for singer in vsingerdict:
        if singer in title:
            singerskey += vsingerdict[singer]

    if singerskey == 0:
        return title

    vsingers = vsingersdict[str(singerskey)]
    titlebackup = title

    if title.find("】") >= 0:
        title = title[title.find("】")+1::]
    if title.find("【") >= 0:
        title = title[:title.find("【"):]

    if len(title) > 0:
        return "-*-".join([title, vsingers, album])
    else:
        return "-*-".join([titlebackup, vsingers, album])
