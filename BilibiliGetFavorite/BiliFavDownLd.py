from urllib import request
import os
from functools import reduce

vmid = ""
fid = ""
avs = ["AV"]
avstitle = ["Title"]
avspic = ["Pic"]
preurl = ""
txtsave = ""
picsave =  ""
videosave = ""
videourl = "https://www.bilibili.com/video/av"
removechr = {"/": "-",
             "\\": "-",
             ":": "-",
             "*": "-",
             "?": "-",
             "<": "-",
             ">": "-",
             "|": "-",
             "：" : "-",
             "\"" : "-",
             "→" : "-"
            }
specialchr = {"\\u0026": "&",
              "\\u003c" : "-",
              "\\u003e" : "-"}
specialchrindex = ["\\u0026","\\u003c","\\u003e"]

def rmvchr(s) :
    if s in removechr :
        return removechr[s]
    else :
        return s


def rplchr(s):
    a = True
    while a :
        a = False
        for i in range(0,len(specialchrindex),1) :
            if specialchrindex[i] in s :
                s = s[:s.find(specialchrindex[i],0):]+specialchr[specialchrindex[i]]+s[s.find(specialchrindex[i],0)+6::]
                a = True
    return s


def getdata(pn) :
    wholeurl = preurl + str(pn)
    wholeHTML = request.urlopen(wholeurl).read().decode("utf-8")
    st = wholeHTML.find("aid",0)+5
    ed = wholeHTML.find(",",st)
    avs.append(wholeHTML[st:ed:])
    st = wholeHTML.find("pic",ed)+6
    ed = wholeHTML.find(",",st)-1
    avspic.append(wholeHTML[st:ed:])
    st = wholeHTML.find("title",ed)+8
    ed = wholeHTML.find(",\"",st)-1
    avstitle.append(wholeHTML[st:ed:])
    return "Finsh"


if __name__=="__main__":
    urlin = input("enter your fav: ")
    vmid = urlin[urlin.find("com", 0) + 4:urlin.find("/#", 0):]
    fid = urlin[urlin.find("fid", 0) + 4:-1:]
    preurl = "https://api.bilibili.com/x/v2/fav/video?vmid=" + vmid + "&ps=1&fid=" + fid + "&pn="
    number = int(input("enter your number: "))
    txtsave = input("enter the path you want to save the data(full path with document name): ")
    picsave = input("enter the path you want to save the pictures(full path): ")
    videosave = input("enter the path you want to save the videos(full path): ")

    for i in range(1, number + 1, 1):
        print(str(i) + " " + getdata(i))

    expt = input("Export Data? y/n ")
    if expt == "y":
        with open(txtsave, "w", encoding="utf-8") as exfile:
            for i in range(0, number + 1, 1):
                avstitle[i] = rplchr(avstitle[i])
                exfile.write((avs[i] + " " + avstitle[i] + " " + avspic[i] + "\n"))
        print("Finish")
    else:
        print("OK")

    downldpic = input("Download Pictures? y/n ")
    if downldpic == "y":
        for i in range(1, number + 1, 1):
            avstitle[i] = reduce(lambda x, y: x + y, map(rmvchr, avstitle[i]))
            os.system("you-get --output-dir %s --output-filename %s %s" % (picsave, avs[i], avspic[i]))
            os.rename(picsave + avs[i] + avspic[i][-4::], picsave + avstitle[i] + avspic[i][-4::])
        print("Finish")
    else:
        print("Ok")

    downld = input("Download Video? y/n ")
    if downld == "y":
        for i in range(1, number + 1, 1):
            os.system("you-get --format=flv -o %s %s" % (videosave, videourl + avs[i]))
        print("Finish")
    else:
        print("Ok")

    print("All Finish")
