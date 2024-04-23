import importlib
import os
required_libraries = ["httpx", "json_minify","flask"]

for library in required_libraries:
    try:
        importlib.import_module(library)
    except ImportError:
        print(f"Installing {library}...")
        import subprocess
        subprocess.call(["pip", "install", library])
        print(f"{library} installed successfully.")
        os.system("clear")


parameters = {
    "community-link":
        "http://aminoapps.com/c/Zwm",
    "proxies": {
        "https://": None
}}
###################
emailFile = "acc.json"
###################



#-----------------FLASK-APP-----------------
from flask import Flask
import random
flask_app = Flask('')
@flask_app.route('/')
def home(): return "~~8;> ~~8;>"
ht = '0.0.0.0'
pt = random.randint(2000, 9000)
def run():
    flask_app.run(host=ht, port=pt)
#----------------------------------------------------





import json
import time
from hmac import new
from os import urandom
from hashlib import sha1
from typing import Union
from threading import Thread
from base64 import b64encode
from time import strftime, gmtime
from httpx import Client as requests
from json_minify import json_minify



class Generator:
    PREFIX = bytes.fromhex("19")
    SIG_KEY = bytes.fromhex("DFA5ED192DDA6E88A12FE12130DC6206B1251E44")
    DEVICE_KEY = bytes.fromhex("E7309ECC0953C6FA60005B2765F99DBBC965C8E9")

    @staticmethod
    def signature(data: Union[str, bytes]) -> str:
        data = data if isinstance(data, bytes) else data.encode("utf-8")
        return b64encode(Generator.PREFIX + new(Generator.SIG_KEY, data, sha1).digest()).decode("utf-8")

    @staticmethod
    def generate_device_id():
        ur = Generator.PREFIX + (urandom(20))
        mac = new(Generator.DEVICE_KEY, ur, sha1)
        return f"{ur.hex()}{mac.hexdigest()}".upper()




class headers:
    def __init__(self, data=None, content_type=None, device: str = None, sig: str = None, sid: str = None, auid: str = None):
        self.headers = dict()
        if device:
            self.headers["NDCDEVICEID"] = device
        if data:
            self.headers["Content-Length"] = str(len(data))
            self.headers["NDC-MSG-SIG"] = Generator.signature(data=data)
        if auid:
            self.headers['AUID'] = auid
        if sid:
            self.headers["NDCAUTH"] = f"sid={sid}"
        if content_type:
            self.headers["Content-Type"] = content_type
        if sig:
            self.headers["NDC-MSG-SIG"] = sig

    def get_headers(self):
        return self.headers



class aminoZ:
    def __init__(self,proxies: dict = None):
      self.device_id = Generator.generate_device_id()
      self.proxies = proxies
      self.comId = None
      self.sid = None
      self.userId = None
      self.secret = None
      self.url = "https://service.aminoapps.com/api/v1/"
      self.DEFAULT_HEADERS = {
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US",
    "Content-Type": "application/x-www-form-urlencoded",
    "User-Agent": "Apple iPhone12,1 iOS v15.5 Main/3.12.2",
    "Host": "service.aminoapps.com",
    "Connection": "keep-alive",
    "NDCLANG": "en"
}
      self.request = requests(headers=self.DEFAULT_HEADERS,http2=True,base_url=self.url,proxies=self.proxies)

    def headers_update(self, data: str = None, content_type: str = None):
      return headers(
            data=data,
            content_type=content_type,
            sid=self.sid,
            auid=self.userId,
            device=Generator.generate_device_id()
        ).get_headers()

    def login(self, email: str, password: str , clientType: int = 100):
      data = json.dumps({
      "email": email,
            "v": 2,
            "secret": f"0 {password}",
            "deviceID": self.device_id,
            "clientType": clientType,
            "action": "normal",
            "timestamp": int(time.time() * 1000)
        })
      response = self.request.post("g/s/auth/login", headers=self.headers_update(data=data, content_type="application/json"), data=data).json()
      try:
        self.sid = response["sid"]
        self.userId = response["auid"]
      except:pass
      return response

    def get_from_link(self, link: str):
      return self.request.get(f"g/s/link-resolution?q={link}", headers=self.headers_update()).json()

    def join_community(self, comId: int, inviteId: str = None):
        data = {"timestamp": int(time.time() * 1000)}
        if inviteId: data["invitationId"] = inviteId
        data = json.dumps(data)

        response = self.request.post(f"x{comId}/s/community/join?sid={self.sid}", data=data, headers=self.headers_update(data=data)).json()
        return response

    def get_wallet_info(self):
        response = self.request.get(f"/g/s/wallet?sid={self.sid}", headers=self.headers_update()).json()
        return response["wallet"]

    def send_active_object(self, comId: int, timers: list=None, tz: int = -time.timezone // 1000):
        data = {
            "userActiveTimeChunkList": timers,
            "timestamp": int(time.time() * 1000),
            "optInAdsFlags": 2147483647,
            "timezone": tz
            }
        data = json_minify(json.dumps(data))
        request = self.request.post(f"x{comId}/s/community/stats/user-active-time?sid={self.sid}", data=data, headers=self.headers_update(data=data)).json()
        return request

    def lottery(self, comId, time_zone: str = -int(time.timezone) // 1000):
        data = json.dumps({
            "timezone": time_zone,
            "timestamp": int(time.time() * 1000)})
        request = self.request.post(f"x{comId}/s/check-in/lottery?sid={self.sid}", data=data, headers=self.headers_update(data=data)).json()
        return request

class Config:
    def __init__(self):
        with open(emailFile, "r") as config:
            self.account_list = [d for d in json.load(config)]



class App:
    def __init__(self):
        self.proxies = parameters["proxies"]
        self.client = aminoZ(proxies=self.proxies)
        info = self.client.get_from_link(parameters["community-link"])
        try: extensions = info["linkInfoV2"]["extensions"]
        except KeyError:
            raise RuntimeError(info.get("api:message"))
        self.comId=extensions["community"]["ndcId"]
        try: self.invitationId = extensions["invitationId"]
        except: self.invitationId = None

    def tzc(self) -> int:
        localhour = strftime("%H", gmtime())
        localminute = strftime("%M", gmtime())
        UTC = {"GMT0": '+0', "GMT1": '+60', "GMT2": '+120', "GMT3": '+180', "GMT4": '+240', "GMT5": '+300', "GMT6": '+360',"GMT7": '+420', "GMT8": '+480', "GMT9": '+540', "GMT10": '+600', "GMT11": '+660', "GMT12": '+720',"GMT13": '+780', "GMT-1": '-60', "GMT-2": '-120', "GMT-3": '-180', "GMT-4": '-240', "GMT-5": '-300',"GMT-6": '-360', "GMT-7": '-420', "GMT-8": '-480', "GMT-9": '-540', "GMT-10": '-600', "GMT-11": '-660'};
        hour = [localhour, localminute]
        if hour[0] == "00": tz = UTC["GMT-1"];return int(tz)
        if hour[0] == "01": tz = UTC["GMT-2"];return int(tz)
        if hour[0] == "02": tz = UTC["GMT-3"];return int(tz)
        if hour[0] == "03": tz = UTC["GMT-4"];return int(tz)
        if hour[0] == "04": tz = UTC["GMT-5"];return int(tz)
        if hour[0] == "05": tz = UTC["GMT-6"];return int(tz)
        if hour[0] == "06": tz = UTC["GMT-7"];return int(tz)
        if hour[0] == "07": tz = UTC["GMT-8"];return int(tz)
        if hour[0] == "08": tz = UTC["GMT-9"];return int(tz)
        if hour[0] == "09": tz = UTC["GMT-10"];return int(tz)
        if hour[0] == "10": tz = UTC["GMT13"];return int(tz)
        if hour[0] == "11": tz = UTC["GMT12"];return int(tz)
        if hour[0] == "12": tz = UTC["GMT11"];return int(tz)
        if hour[0] == "13": tz = UTC["GMT10"];return int(tz)
        if hour[0] == "14": tz = UTC["GMT9"];return int(tz)
        if hour[0] == "15": tz = UTC["GMT8"];return int(tz)
        if hour[0] == "16": tz = UTC["GMT7"];return int(tz)
        if hour[0] == "17": tz = UTC["GMT6"];return int(tz)
        if hour[0] == "18": tz = UTC["GMT5"];return int(tz)
        if hour[0] == "19": tz = UTC["GMT4"];return int(tz)
        if hour[0] == "20": tz = UTC["GMT3"];return int(tz)
        if hour[0] == "21": tz = UTC["GMT2"];return int(tz)
        if hour[0] == "22": tz = UTC["GMT1"];return int(tz)
        if hour[0] == "23": tz = UTC["GMT0"];return int(tz)

    def generation(self, email: str, password: str, device: str) -> None:
        self.email,self.password = email, password
        self.client = aminoZ(proxies=self.proxies)
        try:
            print(f"\n[\033[1;31mcoins-generator\033[0m][\033[1;34mlogin\033[0m][{email}]: {self.client.login(email = self.email, password = self.password)['api:message']}.")
            print(f"Your available coins: {self.client.get_wallet_info()['totalCoins']}.")
            print(f"[\033[1;31mcoins-generator\033[0m][\033[1;36mjoin-community\033[0m]: {self.client.join_community(comId = self.comId, inviteId = self.invitationId)['api:message']}.")
            print(f"[\033[1;31mcoins-generator\033[0m][\033[1;32mlottery\033[0m]: {self.client.lottery(comId = self.comId, time_zone = self.tzc())['api:message']}")
            for i2 in range(24): print(f"[\033[1;31mcoins-generator\033[0m][\033[1;35mmain-proccess\033[0m][{email}]: {self.client.send_active_object(comId = self.comId, timers = [{'start': int(time.time()), 'end': int(time.time()) + 300} for _ in range(50)], tz = self.tzc())['api:message']}."); time.sleep(3.1)
            print(f"[\033[1;31mcoins-generator\033[0m][\033[1;25;32mend\033[0m][{email}]: Finished.")
        except Exception as error: print(f"[\033[1;31mC01?-G3?3R4?0R\033[0m]][\033[1;31merror\033[0m]]: {error}")

    def run(self):
        print("If you have anything bad to say about this code, put it up your ass because I know what to do")
        while True:
            for acc in Config().account_list:
                e = acc['email']
                p = acc['password']
                d = acc['device']
                self.generation(e, p, d)

if __name__ == "__main__":
    Thread(target=run).start()
    App().run()
