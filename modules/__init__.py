from modules.base import registered_modules,registerModule
from config import Config

modules = []


'''
dynamic import mode, more flexible

Require --add-data "modules;modules" parameter in pyinstaller
'''

# from os import getcwd
# from os.path import  basename, isfile, join
# import glob,importlib
#
# for f in glob.glob(join(getcwd(),"modules", "*.py")):
#     name = basename(f)[:-3:]
#     if name == "base" or name == "__init__":
#         pass
#     if isfile(f) and name in Config.useModules and not f.endswith('__init__.py'):
#         importlib.import_module("modules." + name)


# for f in glob.glob(join(getcwd(),"modules", "*.py")):
#     name = basename(f)[:-3:]
#     if isfile(f) and not f.endswith('__init__.py') and name in Config.useModules:
#         for module in importlib.import_module("modules."+name).exports:
#             modules.append(module)

'''
normal import mode, safe to use.

not flexible
'''

from modules.Bilibili import *
from modules.Info import *
from modules.M3U8 import *
from modules.MPV import *
from modules.RealUrl import *
from modules.Search import *
from modules.UniversalDownload import *



for key,val in registered_modules.items():
    if key in Config.useModules:
        modules.extend(val)