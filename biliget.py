from typing import Dict, Any
from functools import reduce
from modules import modules as modulelist
from modules import BaseModule
import sys

def info(msg,offset=0,step=3):
    if isinstance(msg, str):
        print("BilibiliTools > %s" % infoParser(msg,offset=offset,step=step))
        return
    for m in msg:
        info(m,offset=offset+step,step=step)


def infoParser(msg,offset,step):
    if isinstance(msg,str):
        return "{:>{offset}s}".format(msg,offset=len(msg) + offset)
    return map(lambda x:infoParser(x,offset=offset,step=step)
                      if isinstance(x,str)
                      else infoParser(x,offset=offset+step,step=step),
                      msg)

modules: Dict[str, BaseModule] = dict((m.__name__,m()) for m in modulelist)
methods: Dict[str, BaseModule] = {"help":None,
                                  "quit":None}
methods.update(dict((key,m)for m in modules.values() for key in m.getMethod().keys()))



if __name__ == "__main__":
    for module in modules.values():
        module.prepare()
    while True:
        command = input("-> ")
        method = command.split(" ")[0]
        if not method in methods.keys():
            info("Invalid method.")
            continue
        if method == "quit":
            info("Stop console")
            sys.exit()
        if method == "help":
            for key,module in modules.items():
                info("Module-{m_name}: ".format(m_name = key))
                for m,desc in module.getMethod().items():
                    info("%s: %s" %(m, desc),offset=3)
                for m, desc in module.getOptions().items():
                    info(m,offset=6)
                    info(desc,offset=9)
            continue
        methods[method].process(command)