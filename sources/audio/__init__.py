from sources.base import CommonSource


class AudioSource(CommonSource):
    name = "base"

    @classmethod
    def getSourceName(cls):
        return "audio.%s" % cls.name

    @property
    def audio(self):
        return None


    def isValid(self):
        return False