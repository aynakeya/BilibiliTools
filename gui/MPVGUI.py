from tkinter import ttk
import tkinter as tk

from plugins import mpv_lib

class MPVGUI():
    MAX_VOLUME = 128
    instance = None

    @staticmethod
    def getInstance():
        return MPVGUI.instance

    def __init__(self, gui):
        self.gui: gui.GUI = gui
        self.widget = ttk.Frame(self.gui.getTabController())
        self._initialize()

        self.volume = tk.DoubleVar()
        self.progress = tk.IntVar()
        self.mpv_player: mpv_lib.MPV = None

        self._initialize()

    @property
    def volumePercent(self):
        return self.volume.get() / 100

    @property
    def progressPercent(self):
        return self.progress.get() / 100

    def _initialize(self):
        self.gui.getTabController().add(self.widget, text="MPV")

        MPVGUI.instance = self


    def createWidgets(self):
        frame_main = ttk.LabelFrame(self.widget,
                                    text="MPV Player")
        frame_main.grid_columnconfigure(0, weight=1)
        frame_main.grid_columnconfigure(2, weight=1)
        frame_main.pack(fill="both", expand="yes", padx=8, pady=4)

        # ==== Row 0 ====

        frame_row_1 = ttk.Frame(frame_main)
        frame_row_1.grid(column=1, row=0, padx=8, pady=4)

        frame_player = ttk.Frame(frame_row_1,
                                 width=510, height=340)
        frame_player.grid(column=0, row=0, sticky="news")

        self.mpv_player = mpv_lib.MPV(wid=str(int(frame_player.winfo_id())))

        self.mpv_player.observe_property("percent-pos", self._syncProgress)

        # a = biliVideo.initFromUrl("https://www.bilibili.com/video/BV1CK411p7Xs?t=68")
        # a.load()
        # self.play(a.video.url, headers=a.video.headers)

        # ==== Row 2 ====
        frame_row_2 = ttk.Frame(frame_main)
        # frame_main.grid_columnconfigure(0, weight=1)
        # frame_main.grid_columnconfigure(2, weight=1)
        frame_row_2.grid(column=1, row=1, padx=8, pady=4)

        # add volume scale
        progress_scale = ttk.Scale(frame_row_2,
                                 orient=tk.HORIZONTAL,
                                 variable=self.progress,
                                 from_=0,
                                 to=100,
                                 length = 510,
                                 command = self._setProgress)
        progress_scale.grid(column=0, row=0)

        # ==== Row 3 ====

        frame_row_3 = ttk.Frame(frame_main)
        # frame_main.grid_columnconfigure(0, weight=1)
        # frame_main.grid_columnconfigure(2, weight=1)
        frame_row_3.grid(column=1, row=2, padx=8, pady=4)

        # Adding pause Button
        pause_button = ttk.Button(frame_row_3, width=8, text="pause", command=self._pause)
        pause_button.grid(column=2, row=0)

        # Adding play Button
        play_button = ttk.Button(frame_row_3, width=8, text="play", command=self._play)
        play_button.grid(column=1, row=0)

        # Adding stop Button
        play_button = ttk.Button(frame_row_3, width=8, text="stop", command=self._stop)
        play_button.grid(column=0, row=0)

        # add volume scale
        ttk.Label(frame_row_3, text="Volume: ") \
            .grid(column=3, row=0, sticky=tk.W)
        volume_scale = ttk.Scale(frame_row_3,
                                 orient=tk.HORIZONTAL,
                                 variable=self.volume,
                                 from_=0,
                                 to=100,
                                 command=self._setScaleVolume)
        volume_scale.grid(column=4, row=0)
        self.volume.set(64)
        self._setScaleVolume()
        self._pause()

    def play(self,url,**options):
        if options.get("headers") != None:
            headers = options.pop("headers")
            if headers.get("user-agent") != None:
                self.mpv_player._set_property("user-agent",headers.get("user-agent"))
            if headers.get("referer") != None:
                self.mpv_player._set_property("referrer",headers.get("referer"))
            self.mpv_player._set_property("http-header-fields",
                                          self._parseHeader(headers))
        self.mpv_player.play(url)
        self._play()

    def _parseHeader(self,header):
        headerlist = []
        for key,val in header.items():
            if key == "referer":
                headerlist.append("referrer:{}".format(val))
                continue
            headerlist.append("{}:{}".format(key,val))
        return headerlist

    def _play(self):
        self.mpv_player._set_property("pause", False)
        self._syncProgress()

    def _pause(self):
        self.mpv_player._set_property("pause", True)

    def _stop(self):
        self.mpv_player.stop()

    def _setScaleVolume(self,*args):
        self.mpv_player._set_property("volume", self.volumePercent * self.MAX_VOLUME)

    def _setVolume(self,volume):
        self.mpv_player._set_property("volume", volume)

    def _syncProgress(self,*args):
        if self.mpv_player._get_property("percent-pos") == None:
            self.progress.set(0)
        self.progress.set(self.mpv_player._get_property("percent-pos"))

    def _setProgress(self,*args):
        if self.mpv_player._get_property("percent-pos") == None:
            self.progress.set(0)
            return
        self.mpv_player._set_property("percent-pos", self.progress.get())