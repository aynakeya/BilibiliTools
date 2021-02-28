from typing import Iterable


class OptionParser():
    def __init__(self, raw, first=False):
        raw: str
        self.raw = raw
        self.remove_first = not first
        self.command = ""
        self.options = {}
        self.args = []
        self._process()

    def _process(self):
        rawlist = [x for x in self.raw.split(" ") if x != ""]
        self.command = rawlist[0]
        if self.remove_first:
            rawlist = rawlist[1::]
        for seg in rawlist:
            if len(seg) < 1:
                continue
            if seg[0] == "-":
                opt = seg[1::].split("=")
                if len(opt) < 2:
                    self.options[opt[0]] = ""
                self.options[opt[0]] = "=".join(opt[1:])
            else:
                self.args.append(seg)

    def getOption(self, key):
        return self.options.get(key)

    def getEmptyOptionKeyList(self):
        return [key for key in self.options.keys() if self.options[key] == ""]

    def getParsedOptions(self, empty=False, **kwargs):
        ops = {}
        if empty:
            ops = self.options.copy()
        else:
            for key in self.options.keys():
                if self.options[key] != "":
                    ops[key] = self.options[key]
        for key, val in kwargs.items():
            if ops.get(key) != None:
                ops[key] = val(ops[key])
        return ops


class OutputParser():
    def __init__(self, output_func=print):
        self.output_func = output_func

    def print(self, msg, offset, step, prefix=""):
        # if not isinstance(msg, Iterable):
        #     msg = str(msg)
        if isinstance(msg, str):
            self.output_func("{prefix}{msg}".format(prefix=prefix,
                                                    msg=self._parseOffset(msg,
                                                                          offset=offset,
                                                                          step=step)))
            return
        for m in msg:
            self.print(m, offset=offset + step, step=step, prefix=prefix)

    def _parseOffset(self, msg, offset, step):
        if isinstance(msg, str):
            return "{:>{offset}s}".format(msg, offset=len(msg) + offset)
        return map(lambda x: self._parseOffset(x, offset=offset, step=step)
        if isinstance(x, str)
        else self._parseOffset(x, offset=offset + step, step=step),
                   msg)

# a = OptionParser("aa -fdf -page=1")
# print(a.options)
# print(a.getEmptyOptionKeyList())
# print(a.getParsedOptions(page=int))
