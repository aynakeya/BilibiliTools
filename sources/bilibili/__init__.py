from sources.base import CommonSource


class BilibiliSource(CommonSource):
    __source_name__ = "base"

    @classmethod
    def getSourceName(cls):
        return "bilibili.%s" % cls.__source_name__

    @property
    def id(self):
        return None

    def isValid(self):
        return False