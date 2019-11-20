import re

from baseModels import biliVideo, biliVideoList, biliAudio, biliAudioList
import sys, getopt

methodMap = {"audio":biliAudio,
           "audiolist":biliAudioList,
           "video":biliVideo,
           "videolist":biliVideoList}

console_method = ["dl", "help", "quit"]
console_method_desc = {
    "dl": "start to download。\nsupport: video, media list, audio, audio list",
    "help": "show help",
    "quit": "Quit"
}
console_option = ["-l/--lyric", "-q/--quality", "-c/--cover","-d/--danmu","-m/--maxnumber","--ignore"]
console_option_desc = {
    "-l/--lyric": "download lyric (If have)",
    "-c/--cover": "download cover (If have)",
    "-d/--danmu": "download damu (If have)",
    "-m/--maxnumber":"set the max number of audio or video in a playlist you want to download",
    "--ignore":"ignore download anything that is not chosen by user. eg. \"-c --ignore\" will only download cover and skip video file or audio file",
    "--downloader": "use specific downloader.\n"+
                    "Available downloaders:\n"+
                    "· aria - aria2\n· simple - native python downloader",
    "-q/--quality": "choose the quality.\n" +
                    "Available Audio Quality:\n" +
                    "· 2 - 320k 高品质\n· 1 - 196k 标准\n· 0 - 128k 流畅" +
                    "Available Video Video Quality:\n" +
                    "· 116 - 高清 1080P60(SESSDATA required)\n· 112 - 高清 1080P+(SESSDATA required)\n"+
                    "· 80 - 高清 1080P(SESSDATA required)\n· 74 - 高清 720P60\n(SESSDATA required)" +
                    "· 64 - 高清 720P(SESSDATA required)\n· 48 - 高清 720P (MP4)(SESSDATA required)\n"+
                    "· 32 - 清晰 480P\n· 16 - 流畅 360P"
}

def autoSelector(url):
    if re.search(r"am[0-9]+",url) != None:return biliAudioList
    if re.search(r"au[0-9]+",url) != None:return biliAudio
    if re.search(r"av[0-9]+",url) != None:return biliVideo
    if re.search(r"fid=[0-9]+", url) != None: return biliVideoList
    return None

if __name__ == "__main__":
    while True:
        command = input("Download: ")
        method = command.split(" ")[0]
        if not method in console_method:
            print("Invalid method.")
            continue
        if method == "quit":
            print("Stop console")
            sys.exit()
        if method == "help":
            print("Methods:")
            for i in console_method:
                print(i, ":", console_method_desc[i])
            print("\n\n\nOptions")
            for i in console_option:
                print(i, ":", console_option_desc[i])
            continue

        try:
            options, args = getopt.getopt(command.split(" ")[1:], "lcdq:m:", ["lyric", "cover","quality","danmu","downloader","maxnumber","ignore"])
        except:
            print("illegal option")
            continue

        kwargs = {}
        kwargs["qn"] = 116
        for key, value in options:
            if key == "-l" or key == "--lyric":
                kwargs["lyric"] = True
            if key == "-c" or key == "--cover":
                kwargs["cover"] = True
            if key == "-d" or key == "--damu":
                kwargs["damu"] = True
                method = "video"
            if key == "-q" or key == "--quality":
                kwargs["qn"] = value
            if key == "-m" or key == "--maxnumber":
                kwargs["maxNum"] = int(value)
            if key == "--downloader":
                kwargs["downloader"] = value
            if key == "--ignore":
                kwargs["audio"] = False
                kwargs["video"] = False

        for url in [s for s in args if s != ""]:
            print("Start to download %s" % url)
            m = autoSelector(url).initFromUrl(url) if autoSelector(url) != None else None
            if m == None:
                print("Url not support")
                continue
            m.getInfo(**kwargs)
            if m.isValid():
                m.download(**kwargs)
                print("Download finish")
            else:
                print("this url may not be available now")