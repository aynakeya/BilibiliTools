from os.path import dirname, basename, isfile, join
from config import Config
import glob,importlib

from utils.command import OutputParser

modules = []

class RunningMode():
    CONSOLE = "console"
    GUI = "gui"

class BaseModule:
    running_mode = RunningMode.CONSOLE
    output_parser = OutputParser()

    def getMethod(self):
        return {}

    def getOptions(self):
        return {}

    def prepare(self):
        pass

    def require(self):
        pass

    def process(self, args):
        pass

    def info(self,msg,offset=0,step=3,prefix=True):
        if prefix:
            self.output_parser.print(msg,offset,step,
                                     prefix="BilibiliTools - {} >".format(self.__class__.__name__))
        else:
            self.output_parser.print(msg, offset, step)

for f in glob.glob(join(dirname(__file__), "*.py")):
    name = basename(f)[:-3:]
    if isfile(f) and not f.endswith('__init__.py') and name in Config.useModules:
        for module in importlib.import_module("."+name,"modules").exports:
            modules.append(module)

# modules.sort(key=lambda m:Config.useModules.index(m.__name__))