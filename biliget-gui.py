import os

os.environ["PATH"] = os.getcwd() + os.pathsep + os.environ["PATH"]

from gui import GUI
if __name__ == "__main__":
    g = GUI()
    g.createWidgets()
    g.win.mainloop()