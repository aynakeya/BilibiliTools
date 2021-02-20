class OptionParser():
    def __init__(self,raw,first=False):
        raw:str
        self.raw = raw
        self.remove_first = not first
        self.options = {}
        self.args = []
        self._process()


    def _process(self):
        rawlist = [x for x in self.raw.split(" ") if x != ""]
        if self.remove_first:
            rawlist = rawlist[1::]
        for seg in rawlist:
            if len(seg) < 2:
                continue
            if seg[0] == "-":
                opt = seg[1::].split("=")
                if len(opt) < 2:
                    self.options[opt[0]] = ""
                self.options[opt[0]] = "=".join(opt[1:])
            else:
                self.args.append(seg)

    def getOption(self,key):
        return self.options.get(key)

# a = OptionParser("aa -fdf")
# print(a.options)