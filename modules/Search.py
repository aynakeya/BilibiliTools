from modules import BaseModule

from sources.base import  SourceSelector
from sources import *
from utils.command import OptionParser


class Search(BaseModule):
    name = "Search"
    selector = SourceSelector(ImomoeSource)


    def getMethod(self):
        return {"search": "search all source"}

    def getOptions(self):
        return {"-{source name}": ["search the source type by name",
                                   "default is search all source type",
                                   "Available source type: ",
                                   ["· video"]],
                "-source=<source name>": ["specify a source",
                                          "default is search all source",
                                          "Available source:",
                                          [["· {}".format(x)] for x in self.selector.getSourceNames()]],
                "-page=<page>": ["specify which page"]}

    def process(self, args):
        ops = OptionParser(args)
        if (len(ops.args) < 1):
            self.info("no keyword provided")
            return
        keyword = " ".join(ops.args)
        kwargs = ops.getParsedOptions(page=int)
        # target_source: base_source_name
        target_source = ops.getEmptyOptionKeyList()
        target_source = target_source if len(target_source) >0 else None
        if (kwargs.get("source") == None):
            search_sources = self.selector.sources
        else:
            s = self.selector.getByName(kwargs.get("source"))
            if s == None:
                self.info("Source name not support")
                return
            search_sources = [s]
        self.info(" -- Search Results -- ")
        for search_source in search_sources:
            search_results:SearchResults = search_source.search(keyword,
                                                                **kwargs)
            if search_results == None:
                continue
            results = search_results.getResultsBy(base_source_name=target_source)

            self.info(" -- Source:{} -- ".format(search_source.getSourceName()))
            for index,result in enumerate(results,start=1):
                self.info("[{}]: ".format(index),prefix=False)
                self.info("{name}: [{url}] ({sourcename}:{base_source})".format(name=result.filename,
                                                                                url = result.url,
                                                                                sourcename = result.source_name,
                                                                                base_source = result.base_source_name)
                          ,prefix=False)
            self.info(" --  -- ")
        self.info(" -- End Search Result-- ")

exports = [Search]
