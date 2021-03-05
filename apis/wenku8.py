from apis import CommonRequestWrapper, RegExpResponseContainer,SETTING
from config import Config


class API:
    @staticmethod
    def downlaod_api(book_id):
        return "http://dl.wenku8.com/down.php?type=utf8&id={id}".format(id=book_id)

    @staticmethod
    def info_api(book_id):
        return "https://www.wenku8.net/book/{id}.htm".format(id=book_id)


@CommonRequestWrapper
def getBookInfo(book_id: str):
    return ("get",
            API.info_api(book_id),
            {"headers":SETTING.common_header})

def getFileUrl(book_id: str):
    return API.downlaod_api(book_id)

# container = RegExpResponseContainer(getBookInfo("dddd"),
#                                         info=(r"<title>(.*)</title>",
#                                                 lambda x: x[7:-8:]))
#
# print(container.data)
