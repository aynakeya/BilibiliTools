from sources.base import CommonSource


class Wenku8Source(CommonSource):
    name = "base"

    @classmethod
    def getSourceName(cls):
        return "wenku8.%s" % cls.name

    @property
    def id(self):
        return None

    def isValid(self):
        return False