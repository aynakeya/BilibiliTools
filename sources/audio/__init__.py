from sources.base import CommonSource


class AudioSource(CommonSource):
    name = "base"

    @classmethod
    def getSourceName(cls):
        return "audio.%s" % cls.name

    def isValid(self):
        return False