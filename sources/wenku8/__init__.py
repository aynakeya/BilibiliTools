from sources.base import CommonSource


class Wenku8Source(CommonSource):
    __source_name__ = "base"

    @classmethod
    def getSourceName(cls):
        return "wenku8.%s" % cls.__source_name__

    @property
    def id(self):
        return None

    def isValid(self):
        return False