import re, requests, random, os, sys, getopt, time


class songDownloader(object):
    # fileApi = "https://www.bilibili.com/audio/music-service-c/web/url?privilege=2&quality=2&sid=%s"
    fileApi = "http://api.bilibili.com/audio/music-service-c/url?mid=8047632&mobi_app=iphone&platform=ios&privilege=2&quality=%s&songid=%s"
    infoApi = "https://www.bilibili.com/audio/music-service-c/web/song/info?sid=%s"
    # blocked
    # headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0"}
    headers = {"user-agent": "BilibiliClient/2.33.3",
               'Accept': "*/*",
               'Connection': "keep-alive"}

    def __init__(self, sid):
        self.sid = sid
        self.title = ""
        self.author = ""
        self.lyric = ""
        self.cover = ""

    @classmethod
    def initFormUrl(cls, url):
        exp = "au[1-9]\d*"
        sid = re.search(exp, url)
        if sid == None:
            return cls("")
        return cls(sid.group()[2::])

    def getInfo(self):
        try:
            song_data = requests.get(self.infoApi % self.sid, headers=self.headers).json()
            self.title = song_data["data"]["title"]
            self.author = song_data["data"]["author"]
            self.lyric = song_data["data"]["lyric"]
            self.cover = song_data["data"]["cover"]
            return 0
        except:
            return 1

    def getCdns(self, quality=2):
        try:
            song_data = requests.get(self.fileApi % (quality, self.sid), headers=self.headers).json()
            return song_data["data"]["cdns"]
        except:
            return []

    def downloadAudio(self, dir="", quality=2):
        tried = 0
        cdns = self.getCdns(quality=quality)
        if len(cdns) == 0:
            return 3
        try:
            url = random.choice(cdns)
            fmt = ".m4a"
            fmts = [".m4a", ".mp3"]
            for i in fmts:
                if i in url:
                    fmt = i

            pattern = r'[\\/:*?"<>|\r\n]+'
            filename = re.sub(pattern, "-", "-".join([self.title, self.author, self.sid]) + fmt)

            data = requests.get(url, headers=self.headers).content
            while len(data) < 100000:
                if tried >= 5:
                    return 2
                time.sleep(0.5)
                url = random.choice(cdns)
                data = requests.get(url, headers=self.headers).content
                tried += 1

            with open(os.path.join(dir, filename), "wb") as f:
                f.write(data)
            return 0
        except:
            return 2

    def downloadLyric(self, dir=""):
        if self.lyric == "":
            return 3
        try:
            url = self.lyric
            fmt = ".lrc"
            data = requests.get(url, headers=self.headers).content
            pattern = r'[\\/:*?"<>|\r\n]+'
            filename = re.sub(pattern, "-", "-".join([self.title, self.author, self.sid]) + fmt)
            with open(os.path.join(dir, filename), "wb") as f:
                f.write(data)
            return 0
        except:
            return 2


class playlistDownloader(object):
    infoApi = "https://www.bilibili.com/audio/music-service-c/web/song/of-menu?ps=100&sid=%s&pn=%s"
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0"}

    def __init__(self, sid):
        self.sid = sid
        self.songs = []

    @classmethod
    def initFromUrl(cls, url):
        exp = "am[1-9]\d*"
        sid = re.search(exp, url)
        if sid == None:
            return cls("")
        return cls(sid.group()[2::])

    def getSongs(self):
        self.songs = []
        try:
            pn = 1
            api = self.infoApi % (self.sid, "%s")
            while True:
                url = api % pn
                data = requests.get(url, self.headers).json()
                for song in data["data"]["data"]:
                    temp = songDownloader(str(song["id"]))
                    temp.title = song["title"]
                    temp.author = song["author"]
                    temp.lyric = song["lyric"]
                    temp.cover = song["cover"]
                    self.songs.append(temp)

                if data["data"]["pageCount"] == data["data"]["curPage"]:
                    break
                pn += 1
        except:
            pass

    def downloadAll(self, download, quality=2):
        print("---Start download playlist %s" % self.sid)
        print("-" * 10)
        for song in self.songs:
            if song.sid == "":
                printError("song")
                continue
            if download[0]:
                filename = "%s-%s-%s" % (song.sid, song.title, song.author)
                print("Start Download Audio: %s" % filename)
                status = song.downloadAudio(quality=quality)
                printStatus(status, "audio " + filename)
            if download[1]:
                filename = "%s-%s-%s" % (song.sid, song.title, song.author)
                print("Start Download Lyric: %s" % filename)
                status = song.downloadLyric()
                printStatus(status, "lyric " + filename)
            time.sleep(1)

        print("---download playlist %s end" % self.sid)
        print("-" * 10)


class userDownloader(object):
    infoApi = "https://api.bilibili.com/audio/music-service/web/song/upper?ps=30&uid=%s&order=%s&pn=%s"
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:60.0) Gecko/20100101 Firefox/60.0"}

    def __init__(self, uid):
        self.uid = uid
        self.songs = []

    @classmethod
    def initFromUrl(cls, url):
        exp = "space\.bilibili\.com/[1-9]\d*"
        uid = re.search(exp, url)
        if uid == None:
            return cls("")
        return cls(uid.group()[19::])

    def getSongs(self, order=1):
        self.songs = []
        try:
            pn = 1
            api = self.infoApi % (self.uid, order, "%s")
            while True:
                url = api % pn
                data = requests.get(url, self.headers).json()
                for song in data["data"]["data"]:
                    temp = songDownloader(str(song["id"]))
                    temp.title = song["title"]
                    temp.author = song["uname"]
                    temp.lyric = song["lyric"]
                    temp.cover = song["cover"]
                    self.songs.append(temp)

                if data["data"]["pageCount"] == data["data"]["curPage"]:
                    break
                pn += 1
        except:
            pass

    def downloadAll(self, download, quality=2):
        print("---Start download uploaded song of user (uid: %s)" % self.uid)
        print("-" * 10)
        for song in self.songs:
            if song.sid == "":
                printError("song")
                continue
            if download[0]:
                filename = "%s-%s-%s" % (song.sid, song.title, song.author)
                print("Start Download Audio: %s" % filename)
                status = song.downloadAudio(quality=quality)
                printStatus(status, "audio " + filename)
            if download[1]:
                filename = "%s-%s-%s" % (song.sid, song.title, song.author)
                print("Start Download Lyric: %s" % filename)
                status = song.downloadLyric()
                printStatus(status, "lyric " + filename)
            time.sleep(1)

        print("---download songs of user (uid: %s) end" % self.uid)
        print("-" * 10)


def printError(inpt):
    print("download %s fail" % inpt)


def printStatus(status, file):
    if status == 0:
        print("Download %s complete" % file)
    if status == 2:
        print("Download %s fail" % file)
    if status == 3:
        print("Download %s fail, Does not find %s" % (file, file))


if __name__ == "__main__":
    # console_method = ["audio","sid","playlist","help","quit"]
    console_method = ["audio", "playlist", "user", "help", "quit"]
    console_method_desc = {
        "audio": "download a audio file(s) by enter url",
        # "sid":"download a audio file(s) by enter sid (song id)",
        "playlist": "download a playlist",
        "user": "download all the song of a user",
        "help": "show help",
        "quit": "Quit"
    }
    console_options = ["-l/--lyric", "-q/--quality", "--disable-audio"]
    console_options_desc = {
        "-l/--lyric": "download lyric (If have)",
        "-q/--quality": "choose the song quality from 0 to 2, higher the value, higher the quality",
        "--disable-audio": "do not download audio"
    }
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
            for i in console_method:
                print(i, ":", console_method_desc[i])
            for i in console_options:
                print(i, ":", console_options_desc[i])
            continue
        try:
            options, args = getopt.getopt(command.split(" ")[1:], "lq:", ["lyric", "disable-audio"])
        except:
            print("illegal option")
            continue

        download = [True, False]
        quality = "2"
        for key, value in options:
            if key == "-l" or key == "--lyric":
                download[1] = True
            if key == "--disable-audio":
                download[0] = False
            if key == "-q":
                quality = value

        if quality == "1" or quality == "2" or quality == "0":
            pass
        else:
            print("illegal value")
            continue

        if method == "audio":
            for s in args:
                if s == "":
                    continue
                song = songDownloader.initFormUrl(s)
                if song.sid == "":
                    printError(s)
                    continue
                song.getInfo()
                if download[0]:
                    filename = "%s-%s-%s" % (song.sid, song.title, song.author)
                    print("Start Download Audio: %s" % filename)
                    status = song.downloadAudio(quality=quality)
                    printStatus(status, "audio " + filename)
                if download[1]:
                    filename = "%s-%s-%s" % (song.sid, song.title, song.author)
                    print("Start Download Lyric: %s" % filename)
                    status = song.downloadLyric()
                    printStatus(status, "lyric " + filename)

        if method == "playlist":
            for s in args:
                if s == "":
                    continue
                playlist = playlistDownloader.initFromUrl(s)
                if playlist.sid == "":
                    printError(s)
                    continue
                playlist.getSongs()
                playlist.downloadAll(download,quality=quality)

        if method == "user":
            for s in args:
                if s == "":
                    continue
                playlist = userDownloader.initFromUrl(s)
                if playlist.uid == "":
                    printError(s)
                    continue
                playlist.getSongs()
                playlist.downloadAll(download,quality=quality)

# url = "https://www.bilibili.com/audio/au241921"
# a = songDownloader.initFormUrl(url)
# a.getInfo()
# print(a.downloadAudio(quality=1))
# url = "https://www.bilibili.com/audio/am76105?type=2"
# a = playlistDownloader.initFromUrl(url)
# print(a.sid)
# a.getSongs()
# print(len(a.songs))
# a.songs[0].getCdns()
# print(a.songs[0].downloadAudio())
# url = "https://space.bilibili.com/2932528/audio"
# b = userDownloader.initFromUrl(url)
# print(b.uid)
# b.getSongs()
# print(len(b.songs))
# b.songs[0].getCdns()
# print(b.songs[0].downloadAudio())
