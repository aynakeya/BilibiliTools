from config import Config
from models import biliVideoList,biliVideo
import getopt,sys,os

if __name__ == "__main__":
    svrt = Config.saveroute
    number = None
    try:
        options, args = getopt.getopt(sys.argv[1:], "hs:n:", ["help","saveroute=", "number="])
    except:
        print("illegal option")
        sys.exit()
    for key, value in options:
        if key == "-h" or key == "--help":
            print("python biliFavExtracter.py [options] favlink")
            print("Options:\n"
                  "-s/--saveroute=: saveroute\n"
                  "-n/--number=: number you want to export(default: 1)\n")
            print("程序结束")
            sys.exit()
        if key == "-s" or key == "--saveroute":
            if not os.path.exists(str(value)):
                print("Path not exist")
                sys.exit()
            else:
                svrt = str(value)
        if key == "-n" or key == "--number":
            if str(value).isdigit():
                number = int(value)
            else:
                print("Not a correct number")
                sys.exit()
    if len(args) != 1:
        print("No Favorite Link or to much args")
        sys.exit()
    fav = biliVideoList.initFromUrl(args[0])
    if (fav.media_id == ""):
        print("收藏夹链接格式不正确")
        sys.exit()
    if number is not None:
        fav.getInfo(maxNum=number)
    else:
        fav.getInfo()
    with open(os.path.join(svrt,"fav"+fav.media_id+".csv"),"w",encoding="utf-8") as f:
        for v in fav.videos:
            v: biliVideo
            if (v.isValid()):
                f.write(",".join([str(v.aid),v.title,v.uploader,v.cover])+"\n")
    sys.exit()