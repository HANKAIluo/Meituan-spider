import requests, zlib, base64
import random, re, json
from datetime import datetime
from bs4 import BeautifulSoup
from getproxy import get_proxy
import threading

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/56.0.2924.87 Safari/537.36',
           }


class Singleton(object):
    _instance = None
    def __new__(cls, *args, **kw):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls,*args,**kw)
        return cls._instance

class Crawl(Singleton):
    proxy = None
    def __init__(self):
        pass

    def getTime(self):
        """返回从1970.1.1至今的毫秒数"""
        d1 = datetime(1970, 1, 1)
        d2 = datetime.now()
        d3 = int((d2 - d1).total_seconds() * 1000)
        return d3

    def url_encode(self, data):
        """token解码"""
        if isinstance(data, str):
            data = data.replace(" ", "").encode()
            base_data = zlib.compress(data)
            data = base64.b64encode(base_data)
            return data
        else:
            data = str(data)
            return self.url_encode(data)

    def url_decode(self, data):
        """token编码"""
        if isinstance(data, str):
            data = base64.b64decode(data)
            base_data = zlib.decompress(data)
            return base_data

    def get_changecity(self):
        """支持的城市、网址"""
        url = 'http://www.meituan.com/changecity/'
        try:
            response = requests.get(url, headers=headers)
        except:
            print(url, 'connecterror:', response.status_code)
        if response.status_code == 200:
            response.encoding = 'utf-8'
            bs = BeautifulSoup(response.text, 'lxml')
            city = bs.findAll('a', {'class':'link city '})
            cities_link = {}
            for i in city:
                cities_link[i.text] = 'http:' + i.attrs['href']
        return cities_link

    def get_cities_url(self):
        """酒店网址列表"""
        al = {}
        url = 'http://hotel.meituan.com/anshan/'
        try:
            response = requests.get(url, headers=headers, proxies=self.proxy)
            if response.status_code == 200:
                response.encoding = 'utf-8'
                link = BeautifulSoup(response.text,'lxml')
                all_link = link.findAll('a', {'data-v-641f935a': ''})[97:-342]
                for y in range(1,len(all_link)):
                    al[all_link[y].text] = all_link[y].attrs['href']    #KEY为地名，VALUE为网址的dict
        except Exception as e:
            print(e)
            print(url)
        return al

    def get_hotel_list(self, url):
        """生成城市中所有的酒店网址"""
        hotel_list = []
        try:
            response = requests.get(url, headers=headers, proxies=self.proxy)
            if response.status_code == 200 :
               response.encoding = 'utf-8'
               bs = BeautifulSoup(response.text, 'lxml')
               hotel_link = bs.findAll('li',{'class':'page-link'})[-1].text
               hotel_link = int(hotel_link) + 1
               for t in range(1, hotel_link):
                   if t == 1:
                       pass
                   else:
                        try:
                            url = url + 'pn' + t + '/'
                            response = requests.get(url, headers)
                            response.encoding = 'utf-8'
                            bs = BeautifulSoup(response.text,'lxml')
                        except:
                            pass
                        if response.status_code == 200:
                            lin = bs.findAll('a', {'class': 'poi-title'})
                            for n in lin:
                                net = n.attrs['href']
                                hotel_list.append(net)
        except Exception as e :
            print(e)
            print(url)
        return hotel_list

    def crawl(self,url):
        """抓取酒店数据"""
        data_list = []
        try:
            response = requests.get(url, headers=headers, proxies=self.proxy, timeout=2.0)
            response.encoding = 'utf-8'
            bs = BeautifulSoup(response.text, 'lxml')
            data = [i.text for i in bs.findAll('span') ]
            city = bs.findAll('a',{'class':'breadcrumb-item'})[0].text
            data_list = [city, url, data[10], data[12], data[15],data[38]]
        except Exception as e:
            print(e)
            print(url)
            return None
        cookies_iuuid = ['93AB5D4FEB3D1BFFF9B7727E5ECE71CF13A51383CD6ADB169C43832A6BB41843',
                         '8A8E20A923D42E033BC3505E3460BCC25AEA4D933CE3F233B19679BB0EEC89D4',
                         'C68174784AF5C11CC2F127774CC8BA60FB5E766509A7DCA8F4ECDFF59B45076F',
                         '850C1A14A798DC5834EEF2177EAAA430A8958DBE0813C5FAE858B61834D1F95D']
        taken = {}
        taken["poiId"] = re.findall(r'"poiId":[0-9]*', response.text)[0][8:]
        taken["start"] = re.findall(r'"queryStart":[0-9]*', response.text)[0][13:]
        taken["end"] = re.findall(r'"queryEnd":[0-9]*',response.text)[0][11:]
        taken["?type"] = "1"
        taken["&utm_medium"] = "PC"
        taken["version_name"] = "7.3.0"
        taken["uuid"] = cookies_iuuid[random.randint(0,3)]
        sign = "\"end=" + taken["end"] + "&poiId=" + taken["poiId"] + "&start=" + taken["start"] + "&type=1&" \
                "utm_medium=PC&uuid=" + taken["uuid"] + "&version_name=" + taken["version_name"] +"\""
        _tokon = json.dumps({"rId":100051,
                  "ts":self.getTime(),
                  "cts":self.getTime()+462,
                  "brVD":[1920,502],
                  "brR":[[1920,1080],[1920,1040],24,24],
                  "b":[url,""],
                  "mT":[],
                  "kT":[],
                  "aT":[],
                  "tT":[],
                  "sign":self.url_encode(sign).decode()})
        t = "https://ihotel.meituan.com/productapi/v2/prepayList?type=1&utm_medium=PC&version_name=" \
                "7.3.0&poiId=" + taken["poiId"] + "&start=" + \
        taken["start"] + "&end=" + taken["end"] + "&uuid=" + taken["uuid"] + "&_token=" + \
        self.url_encode(_tokon).decode()
        try:
            res = requests.get(t, headers=headers, proxies=self.proxy, timeout=2.0)
            data_list.append(int(re.findall(r'lowestPrice":[0-9]+', res.text)[0][13:]) / 100)  # 最低价格（并没有神马卵用）
        except Exception as e:
            print(e)
            print(t)
            return None
        return data_list

if __name__ == '__main__':
    proxy = next(get_proxy())
    print(proxy)
    n =Crawl()
    n.proxy=proxy
    t = n.get_hotel_list('http://hotel.meituan.com/beijing/')
    #t=n.crawl(city='广州',url='http://hotel.meituan.com/1211661/')
    print(t)