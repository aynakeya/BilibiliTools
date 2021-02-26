from utils.command import OutputParser

registered_modules = {}

def registerModule(func):
    name = ".".join(func.__module__.split(".")[1::])
    if name in registered_modules.keys():
        registered_modules[name].append(func)
    else:
        registered_modules[name] = [func]
    return name

def registerModuleByName(name):
    def wrapper(func):
        if name in registered_modules.keys():
            registered_modules[name].append(func)
        else:
            registered_modules[name] = [func]
        return func
    return wrapper

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