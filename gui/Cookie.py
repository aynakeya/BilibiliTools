from tkinter import ttk, scrolledtext
import tkinter as tk
import gui
from config import Config


class CookieGUI():
    def __init__(self,gui):
        self.gui: gui.GUI = gui
        self.widget = ttk.Frame(self.gui.getTabController())
        self.cookie_host = tk.StringVar()
        self.cookie_content: scrolledtext.ScrolledText = None
        self._initialize()

    def _initialize(self):
        self.gui.getTabController().add(self.widget,text = "Cookie")

    def createWidgets(self):
        frame_main = ttk.LabelFrame(self.widget, text="Edit Cookie")
        frame_main.grid(column=0, row=0, padx=8, pady=4)

        # ========== input frame ================

        frame_input = ttk.Frame(frame_main)
        frame_input.grid(column=0, row=0, padx=8, pady=4,sticky=tk.W)

        # Creating check box for commands
        ttk.Label(frame_input, text="Select Cookie:") \
            .grid(column=0, row=0, sticky=tk.W, padx=8, pady=4)
        cookie_chosen = ttk.Combobox(frame_input,
                                     width=16,
                                     textvariable=self.cookie_host,
                                     state='readonly')
        cookie_chosen['values'] = tuple(Config.cookies.keys())
        cookie_chosen \
            .grid(column=1, row=0, padx=8, pady=4)
        cookie_chosen.current(0)

        cookie_chosen.bind('<<ComboboxSelected>>',self._loadCookie)

        # Adding a Button
        action = ttk.Button(frame_input, width=8, text="load", command = self._loadCookie)
        action.grid(column=2, row=0, padx=8, pady=4)

        # Adding a Button
        action = ttk.Button(frame_input, width=8, text="reload",command = self._loadCookie)
        action.grid(column=3, row=0, padx=8, pady=4)

        # Adding a Button
        action = ttk.Button(frame_input, width=8, text="save", command = self._saveCookie)
        action.grid(column=4, row=0, padx=8, pady=4)

        # ========== edit frame ===============
        frame_edit = ttk.Frame(frame_main)
        frame_edit.grid(column=0, row=1, padx=8, pady=4)
        # Using a scrolled Text control
        scrol_w = 64 + 32
        scrol_h = 16
        self.cookie_content = scrolledtext.ScrolledText(frame_edit,
                                                width=scrol_w,
                                                height=scrol_h,
                                                state=tk.NORMAL,
                                                wrap=tk.CHAR)
        self.cookie_content.grid(column=0, padx=8, pady=4)

        self._loadCookie()

    def _clearContent(self,*args):
        self.cookie_content.delete(0.0, tk.END)

    def _loadCookie(self,*args):
        self._clearContent()
        data = Config.getCookie(self.cookie_host.get())
        string = ";".join("{}={}".format(key,val) for key,val in data.items())
        self.cookie_content.insert("end",
                                   "%s\n" % string)

    def _saveCookie(self,*args):
        datastring = self.cookie_content.get(0.0,tk.END).replace("\n","")
        for keyval in [x.split("=") for x in datastring.split(";") if x != ""]:
            if (len(keyval) < 2):
                continue
            key = keyval[0]
            val = "=".join(keyval[1:])
            Config.getCookie(self.cookie_host.get())[key] = val
        Config.saveCookie()
        self._loadCookie()