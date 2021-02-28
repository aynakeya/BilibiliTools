from sources.base import CommonSource


class VideoSource(CommonSource):
    __source_name__ = "base"

    @classmethod
    def getSourceName(cls):
        return "video.%s" % cls.__source_name__

    @property
    def video(self):
        return None


    def isValid(self):
        return False