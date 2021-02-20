from sources.base import CommonSource


class VideoSource(CommonSource):
    name = "base"

    @classmethod
    def getSourceName(cls):
        return "video.%s" % cls.name

    def isValid(self):
        return False