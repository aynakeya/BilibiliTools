from sources.base import CommonSource


class BilibiliSource(CommonSource):
    name = "base"

    downloadable = False
    watchable = False

    @classmethod
    def getSourceName(cls):
        return "bilibili.%s" % cls.name

    @property
    def id(self):
        return None

    def isValid(self):
        return False