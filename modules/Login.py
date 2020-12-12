from modules import BaseModule
from config import Config
from utils import QrLogin

class Login(BaseModule):

    def getMethod(self):
        return {"qrlogin":"get cookie using qrcode login"}

    def prepare(self):
        if Config.commonCookies["SESSDATA"] == "":
            if input("We found that there is no sessdata included, would you like to login using qrcode y/n ?") == "y":
                QrLogin.manuallylogin()

    def process(self, args):
        QrLogin.manuallylogin()

module = Login