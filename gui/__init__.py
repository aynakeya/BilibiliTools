from mttkinter import mtTkinter as tk
from tkinter import ttk
from tkinter import Menu
from tkinter.ttk import Notebook
from typing import Dict

from gui.Config import ConfigGUI
from gui.Console import ConsoleGUI
from gui.Cookie import CookieGUI
from gui.MPVGUI import MPVGUI
from modules import BaseModule
from modules import modules as modulelist
from sources import biliVideo


class GUI():
    def __init__(self):
        self.win = tk.Tk()
        self.win.title("Ayna Downloader")
        self.tab_controller: Notebook = ttk.Notebook(self.win)
        self.menuc_controller = Menu(self.win)
        self._initialize()

    def _initialize(self):
        self.win.resizable(False,False)
        self.win.geometry("720x480")
        self.tab_controller.pack(expand = 1,fill="both")

    def getTabController(self) -> Notebook:
        return self.tab_controller

    def start(self):
        self.win.mainloop()

    def createWidgets(self):
        ConsoleGUI(self).createWidgets()
        ConfigGUI(self).createWidgets()
        CookieGUI(self).createWidgets()
        MPVGUI(self).createWidgets()




