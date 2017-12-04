from urllib import request
import os

vmid = ""
fid = ""
avs = ["AV"]
avstitle = ["Title"]
avspic = ["Pic"]
preurl = ""
videosave = ""
videourl = "https://www.bilibili.com/video/av"
txtsave = ""


urlin = input("enter your fav: ")
vmid = urlin[urlin.find("com",0)+4:urlin.find("/#",0):]
fid = urlin[urlin.find("fid",0)+4:-1:]
preurl = "https://api.bilibili.com/x/v2/fav/video?vmid="+vmid+"&ps=1&fid="+fid+"&pn="
number = int(input("enter your number: "))
videosave = input("enter the path you want to save the videos(full path): ")
txtsave = input("enter the path you want to save the data(full path with document name): ")


def GetData(pn) :
    wholeurl = preurl + str(pn)
    wholeHTML = request.urlopen(wholeurl).read().decode("utf-8")
    st = wholeHTML.find("aid",0)+5
    ed = wholeHTML.find(",",st)
    avs.append(wholeHTML[st:ed:])
    st = wholeHTML.find("pic",ed)+6
    ed = wholeHTML.find(",",st)-1
    avspic.append(wholeHTML[st:ed:])
    st = wholeHTML.find("title",ed)+8
    ed = wholeHTML.find(",",st)-1
    avstitle.append(wholeHTML[st:ed:])
    return "Finsh"


for i in range(1,number+1,1) :
    print(str(i)+" "+GetData(i))

expt = input("Export Data? y/n ")

if expt == "y" :
    with open(txtsave, "w", encoding="utf-8") as exfile :
        for i in range(0, number + 1, 1) :
            exfile.write((avs[i]+" "+avstitle[i]+" "+avspic[i]+"\n"))
else :
    print("OK")

downld = input("Download Video? y/n ")

if downld == "y" :
    for i in range(1,number+1,1) :
        #print("you-get --format=flv -o %s -0 %s %s" % (videosave,avstitle[i],videourl+avs[i]))
        os.system("you-get --format=flv -o %s %s" % (videosave,videourl+avs[i]))
else :
    print("Ok")

print("Work Finsh")