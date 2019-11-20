import mutagen
from mutagen.mp4 import MP4,MP4Cover
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC


class infoEditor():
    def __init__(self, file):
        self.file = file
        self.audio = None
        self.titleTag = None
        self.artistTag = None

    @staticmethod
    def initialize(file):
        audio = mutagen.File(file)
        if (isinstance(audio, MP4)):
            return mp4Editor(file)
        if (isinstance(audio, MP3)):
            return mp3Editor(file)

    def isValid(self):
        return False

    @property
    def title(self):
        return self.audio.tags.get(self.titleTag)

    @title.setter
    def title(self, title):
        self.audio.tags[self.titleTag] = title

    @property
    def artist(self):
        return self.audio.tags.get(self.artistTag)

    @artist.setter
    def artist(self, artist):
        self.audio.tags[self.artistTag] = artist

    def writePicture(self, img):
        pass

    def save(self):
        self.audio.save()

    def reload(self):
        pass


class mp3Editor(infoEditor):
    def __init__(self, file):
        super().__init__(file)
        self.audio = MP3(file, ID3=EasyID3)  # type: MP3
        self.titleTag = "title"
        self.artistTag = "artist"

    def writePicture(self, img):
        try:
            id3 = ID3(self.file)
            with open(img, 'rb') as pic:
                mine = "image/png" if img.split(".")[-1].lower() == "png" else "image/jpeg"
                id3['APIC'] = APIC(
                    # encoding=3,
                    mime=mine,
                    # type=3, desc=u'Cover',
                    data=pic.read()
                )
            id3.save()
            self.reload()
        except:
            pass

    def reload(self):
        self.audio = MP3(self.file, ID3=EasyID3)


class mp4Editor(infoEditor):
    def __init__(self, file):
        super().__init__(file)
        self.audio = MP4(file)  # type: MP4
        self.titleTag = "\xa9nam"
        self.artistTag = "\xa9ART"

    def writePicture(self, img):
        try:
            with open(img, 'rb') as pic:
                if (img.split(".")[-1].lower() == "jpg"):
                    self.audio['covr'] = [MP4Cover(pic.read(), imageformat=MP4Cover.FORMAT_JPEG)]
                elif (img.split(".")[-1].lower() == "png"):
                    self.audio['covr'] = [MP4Cover(pic.read(), imageformat=MP4Cover.FORMAT_PNG)]
                else:
                    self.audio['covr'] = [MP4Cover(pic.read())]
            self.save()
        except:
            pass

    def reload(self):
        self.audio = MP4(self.file)