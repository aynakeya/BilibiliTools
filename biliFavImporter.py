from models import biliVideoList,biliVideo
import getopt,sys,os,time

if __name__ == "__main__":
    try:
        options, args = getopt.getopt(sys.argv[1:], "d:a:", ["data="])
    except:
        print("illegal option")
        sys.exit()
    aids = []
    for key, value in options:
        if key == "-d" or key == "--data":
            if os.path.exists(value):
                with open(value,"r",encoding="utf-8") as f:
                    aids.extend([l.split(",")[0] for l in f.readlines() if l.split(",")[0].isdigit()])

        if key == "-a":
            aids.extend([l for l in value.split(",") if l.isdigit()])

    if len(args) <1:
        print("没有输入收藏夹链接")
    fav = biliVideoList.initFromUrl(args[0])
    if (fav.media_id == ""):
        print("收藏夹链接格式错误")
        sys.exit()
    for aid in aids:
        resp = fav.addVideo(aid)
        print(aid, resp)
        if resp is None:
            continue
        trail = 1
        while resp["code"] == -509 and trail < 5:
            print("暂停")
            time.sleep(3)
            resp = fav.addVideo(aid)
            print(aid, resp)
            if resp is None:
                trail = 100
