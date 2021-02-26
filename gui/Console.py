import tkinter as tk
from tkinter import ttk, scrolledtext

from config import Config
from modules import modules as modulelist, RunningMode
from modules import BaseModule
from typing import Dict
from downloaders import downloaders as downloaderlist
from utils.command import OutputParser


class ConsoleGUI():
    modules: Dict[str, BaseModule] = dict((m.name, m()) for m in modulelist)
    methods: Dict[str, BaseModule] = {"help": None}
    methods.update(dict((key, m) for m in modules.values() for key in m.getMethod().keys()))
    target_source_list = ["video", "audio", "text", "lyric", "cover", "danmu"]
    target_source_default = ["video"]

    output_parser = OutputParser()

    def __init__(self, gui):
        self.gui: gui.GUI = gui
        self.widget = ttk.Frame(self.gui.getTabController())
        self.args = tk.StringVar()
        self.method = tk.StringVar()
        self.downloader = tk.StringVar()
        self.output: scrolledtext.ScrolledText = None
        self.target_sources = dict(
            zip(self.target_source_list, [tk.IntVar() for i in range(len(self.target_source_list))]))

        self._initialize()

    def _initialize(self):
        self.gui.getTabController().add(self.widget, text="Conole")

        BaseModule.output_parser.output_func = self._info
        BaseModule.running_mode = RunningMode.GUI

        self.output_parser.output_func = self._info

        for module in self.modules.values():
            module.prepare()

    def createWidgets(self):
        frame_main = ttk.LabelFrame(self.widget, text="Console")
        frame_main.grid(column=0, row=0, padx=8, pady=4)

        # ========== input frame ================

        frame_input = ttk.Frame(frame_main)
        frame_input.grid(column=0, row=0, padx=8, pady=4)

        # ==== Row 0 ====
        frame_basic = ttk.Frame(frame_input)
        frame_basic.grid(column=0, row=0, padx=8, pady=4)
        # Creating check box for commands
        ttk.Label(frame_basic, text="Command:") \
            .grid(column=0, row=0, sticky=tk.W, padx=8, pady=4)
        method_chosen = ttk.Combobox(frame_basic, width=16, textvariable=self.method, state='readonly')
        method_chosen['values'] = tuple(self.methods.keys())
        method_chosen \
            .grid(column=0, row=1, padx=8, pady=4)

        if (len(self.methods.keys()) > 0):
            method_chosen.current(0)

        # Creating check box for commands
        ttk.Label(frame_basic, text="Enter a urls:") \
            .grid(column=1, row=0, sticky=tk.W, padx=8, pady=4)
        parameter_entry = ttk.Entry(frame_basic, width=64, textvariable=self.args)
        parameter_entry.grid(column=1, row=1,
                             padx=8, pady=4)

        # Adding a Button
        action = ttk.Button(frame_basic, width=8, text="Execute", command=self._executeCommand)
        action.grid(column=2, row=1)

        # ==== End Row 0 ====

        # ==== Row 1 ====
        # add source list
        frame_row1 = ttk.Frame(frame_input)
        frame_row1.grid(column=0, row=1,
                          padx=8, pady=4, sticky=tk.W)

        frame_row1_source = ttk.Frame(frame_row1)
        frame_row1_source.grid(column=0, row=0,
                               padx=8, pady=4, sticky=tk.W)

        frame_row1_downloader = ttk.Frame(frame_row1)
        frame_row1_downloader.grid(column=1, row=0,
                                   padx=8, pady=4, sticky=tk.W)

        ttk.Label(frame_row1_source, text="Select Target Sources:") \
            .grid(column=0, row=0,
                  columnspan=len(self.target_source_list),
                  sticky=tk.W)

        for index, key in enumerate(self.target_source_list):
            check = tk.Checkbutton(frame_row1_source,
                                   text=key,
                                   variable=self.target_sources.get(key))
            check.grid(column=index, row=1, sticky=tk.W)
            if key in self.target_source_default:
                check.select()

        ttk.Label(frame_row1_downloader, text="Select Downloader:") \
                .grid(column=0, row=0, sticky=tk.W)
        downloader_chosen = ttk.Combobox(frame_row1_downloader,
                                         width=16, textvariable=self.downloader,
                                         state='readonly')
        downloader_chosen['values'] = tuple(downloaderlist.keys())
        downloader_chosen \
            .grid(column=0, row=1)
        downloader_chosen.current(list(downloaderlist.keys()).index(Config.defaultDownloader))

        # ========== output frame ===============
        frame_output = ttk.Frame(frame_main)
        frame_output.grid(column=0, row=2, padx=8, pady=4)
        # Using a scrolled Text control
        scrol_w = 64 + 32
        scrol_h = 16
        self.output = scrolledtext.ScrolledText(frame_output,
                                                width=scrol_w,
                                                height=scrol_h,
                                                state=tk.DISABLED,
                                                wrap=tk.WORD)
        self.output.grid(column=0, padx=8, pady=4, columnspan=3)

    def _parseTargetSource(self):
        s = []
        for key, value in self.target_sources.items():
            if value.get() == 1:
                s.append("-{}".format(key))
        return " ".join(s)

    def _executeCommand(self):
        method = self.method.get()
        command = "{cmd} {sources} {downloader} {args}".format(cmd=self.method.get(),
                                                  sources=self._parseTargetSource(),
                                                  downloader = "-downloader={}".format(self.downloader.get()),
                                                  args=self.args.get())
        if method == "help":
            for key, module in self.modules.items():
                self.info("Module-{m_name}: ".format(m_name=key))
                for m, desc in module.getMethod().items():
                    self.info("%s: %s" % (m, desc), offset=3)
                for m, desc in module.getOptions().items():
                    self.info(m, offset=6)
                    self.info(desc, offset=9)
            return
        self.methods[method].process(command)

    def info(self,msg,offset=0, step=3):
        self.output_parser.print(msg,offset,step,prefix="BilibiliTools > ")

    def _clearOutput(self):
        self.output.config(state=tk.NORMAL)
        self.output.delete(0.0, tk.END)
        self.output.config(state=tk.DISABLED)

    def _info(self, msg):
        self.output.config(state=tk.NORMAL)
        self.output.insert("end", "%s\n" % msg)
        self.output.see("end")
        self.output.config(state=tk.DISABLED)
        # if isinstance(msg, str):
        #     self.output.config(state=tk.NORMAL)
        #     self.output.insert("end", "%s\n" % self._infoParser(msg, offset=offset, step=step))
        #     self.output.config(state=tk.DISABLED)
        #     return
        # for m in msg:
        #     self._info(m, offset=offset + step, step=step)

    def _infoParser(self, msg, offset, step):
        if isinstance(msg, str):
            return "{:>{offset}s}".format(msg, offset=len(msg) + offset)
        return map(lambda x: self._infoParser(x, offset=offset, step=step)
        if isinstance(x, str)
        else self._infoParser(x, offset=offset + step, step=step),
                   msg)
