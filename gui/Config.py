from tkinter import ttk

import gui


class ConfigGUI():
    def __init__(self,gui):
        self.gui: gui.GUI = gui
        self.widget = ttk.Frame(self.gui.getTabController())
        self._register()

    def _register(self):
        self.gui.getTabController().add(self.widget,text = "Config")

    def createWidgets(self):
        pass