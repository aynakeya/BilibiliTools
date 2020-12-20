from modules import BaseModule
from models import modelSelector
from config import Config
import subprocess
class MPV(BaseModule):

    def getMethod(self):
        return {"mpv": "Play by mpv"}

    def mpvHeaderString(self,headers:dict):
        return "--http-header-fields=%s" % \
                  ",".join("\"%s:%s\"" %(x,y) for x,y in headers.items())


    def playByMPV(self,model):
        playurl = model.getPlayurl()
        if (playurl == None):
            self.info("无法获取到视频源地址，可能是没开带会员")
            return
        title = model.outputTitle("video",model.currentPage,"")[:-1:]
        headers={"origin": "www.bilibili.com", "referer": model.videoUrl % model.bid,
                                         "user-agent": Config.commonHeaders["user-agent"]}
        subprocess.Popen("mpv --force-media-title=\"%s\" %s \"%s\"" %(title,self.mpvHeaderString(headers),playurl["urls"][0]))


    def process(self, args):
        args = args.split(" ")[1:]
        if (len(args) < 1):
            self.info("no url provided")
            return
        url = args[0]
        m = modelSelector(url).initFromUrl(url) if modelSelector(url) != None else None
        if m == None:
            self.info("%s not support" % url)
            return
        if m.name != "video" and m.name !="bangumi":
            self.info("%s not support" % url)
            return
        m.getInfo()
        if m.isValid():
            self.info("starting mpv")
            self.playByMPV(m)
        else:
            self.info("this url may not be available now")


module = MPV