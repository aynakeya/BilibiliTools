from os.path import dirname, basename, isfile, join
from config import Config
import glob,importlib
modules = []

class BaseModule:
    running_mode = "console"
    output_func = print

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

    def info(self,msg,prefix=True):
        if prefix:
            self.output_func("BilibiliTools - %s > %s" %(self.__class__.__name__,msg))
        else:
            self.output_func(msg)

for f in glob.glob(join(dirname(__file__), "*.py")):
    name = basename(f)[:-3:]
    if isfile(f) and not f.endswith('__init__.py') and name in Config.useModules:
        for module in importlib.import_module("."+name,"modules").exports:
            modules.append(module)

# modules.sort(key=lambda m:Config.useModules.index(m.__name__))