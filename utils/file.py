import os
import re


def parseFilename(filename):
    pattern = r'[\\/:*?"<>|\r\n]+'
    return re.sub(pattern,"-",filename)


def writeToFile(content,route,name,binary=False):
    path = os.path.join(route, parseFilename(name))
    if not os.path.exists(route):
        os.mkdir(route)
    if binary:
        print(path)
        with open(path, "wb+") as f:
            f.write(content)
    else:
        with open(path, "w+") as f:
            f.write(content)

def getSuffixByUrl(url):
    return url.split(".")[-1]