from config import Config
from downloaders import downloaders as adls
from models import models as amdls
from utils import videoIdConvertor
import re, sys, getopt

availableDl = {}

console_method = ["dl", "help", "convert", "quit"]
console_method_desc = {
    "dl": "start to download。\n    support: video, media list, audio, audio list",
    "help": "show help",
    "convert" : "convert between bv and av",
    "quit": "Quit"
}
console_option = ["-l/--lyric", "-q/--quality", "-c/--cover", "-d/--danmu", "-m/--maxnumber", "--ignore",
                  "--downloader"]
console_option_desc = {
    "-l/--lyric": "download lyric (If have)",
    "-c/--cover": "download cover (If have)",
    "-d/--danmu": "download damu (If have)",
    "-m/--maxnumber": "set the max number of audio or video in a playlist you want to download",
    "--ignore": "ignore download anything that is not chosen by user. eg. \"-c --ignore\" will only download cover and skip video file or audio file",
    "--downloader": "use specific downloader.\n" +
                    "Available downloaders:\n" +
                    "· aria2 - aria2\n· requests - native requests downloader",
    "-q/--quality": "choose the quality.\n" +
                    "Available Audio Quality:\n" +
                    "· 2 - 320k 高品质\n· 1 - 196k 标准\n· 0 - 128k 流畅\n" +
                    "Available Video Video Quality:\n" +
                    "· 116 - 高清 1080P60(SESSDATA required)\n· 112 - 高清 1080P+(SESSDATA required)\n" +
                    "· 80 - 高清 1080P(SESSDATA required)\n· 74 - 高清 720P60(SESSDATA required)\n" +
                    "· 64 - 高清 720P(SESSDATA required)\n· 48 - 高清 720P (MP4)(SESSDATA required)\n" +
                    "· 32 - 清晰 480P\n· 16 - 流畅 360P"
}


def initDownloaders():
    for dl in Config.useDownloader:
        if adls.get(dl) is not None:
            availableDl[adls.get(dl).name] = adls.get(dl)()


def autoSelector(url):
    for m in amdls.values():
        if m.applicable(url):
            return m
    return None


if __name__ == "__main__":
    initDownloaders()
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
            print("\nMethods:")
            for i in console_method:
                print(i, ":", console_method_desc[i])
            print("\nOptions")
            for i in console_option:
                print(i, ":", console_option_desc[i])
            continue
        if method == "convert":
            for url in command.split(" ")[1:]:
                urla = videoIdConvertor.urlConvert(url)
                if urla == "":
                    continue
                print("%s -> %s" % (url, urla))
            continue

        try:
            options, args = getopt.getopt(command.split(" ")[1:], "lcdq:m:",
                                          ["lyric", "cover", "quality=", "danmu", "downloader=", "maxnumber=",
                                           "ignore"])
        except:
            print("illegal option")
            continue

        kwargs = {}
        # todo default config
        kwargs["qn"] = Config.defaultQuality
        kwargs["downloader"] = availableDl.get(Config.defaultDownloader)
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
                kwargs["downloader"] = availableDl.get(value)
            if key == "--ignore":
                kwargs["audio"] = False
                kwargs["video"] = False

        if kwargs["downloader"] == None:
            print("Downloader didn't found")
            continue

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
