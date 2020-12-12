from modules import BaseModule
from models import modelSelector
class Info(BaseModule):

    def getMethod(self):
        return {"info": "Print out basic information."}

    def process(self, args):
        for url in [s for s in args.split(" ")[1:] if s != ""]:
            self.info("Start to get information of %s" % url)
            m = modelSelector(url).initFromUrl(url) if modelSelector(url) != None else None
            if m == None:
                self.info("Url %s not support" % url)
                continue
            m.getInfo()
            if m.isValid():
                self.info("--")
                for key, value in m.dumpInfo():
                    print("%s: %s" % (key,value))
                self.info("--")
            else:
                self.info("Url %s may not be available now" % url)

module = Info