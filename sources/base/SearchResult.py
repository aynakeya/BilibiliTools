from typing import List

from sources.base import BaseSource


class SearchResult(BaseSource):
    __source_name__ = "search-result"

    def __init__(self, url, headers, filename,source,source_name,base_source_name):
        self.url = url
        self.headers = headers
        self.filename = filename
        self.source = source
        self.source_name = source_name
        self.base_source_name = base_source_name

class SearchResults(BaseSource):
    name = "search-results"

    def __init__(self, results:List[SearchResult],current_page,total_page):
        self.results = results
        self.current_page = current_page
        self.total_page = total_page

    def isEmpty(self) -> bool:
        return len(self.results) == 0

    def getResultsBy(self,source_name=None,base_source_name=None):
        rs = self.results
        if source_name != None:
            if isinstance(source_name,List):
                rs = filter(lambda x:x.source_name in source_name,rs)
            elif isinstance(source_name,str):
                rs = filter(lambda x:x.source_name == source_name,rs)
        if base_source_name != None:
            if isinstance(base_source_name,List):
                rs = filter(lambda x:x.base_source_name in base_source_name,rs)
            elif isinstance(base_source_name,str):
                rs = filter(lambda x:x.base_source_name == base_source_name,rs)
        return rs