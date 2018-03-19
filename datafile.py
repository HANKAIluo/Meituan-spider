import os, sys
import csv
import threading
from queue import Queue

LOCK = threading.Lock()

class Singleton(object):
    """单利模式"""
    _instance = None
    def __new__(cls, *args,**kw):
        if not cls._instance:
            cls._instance = super(Singleton, cls).__new__(cls,*args,**kw)
        return cls._instance

class Datafile(Singleton):
    def __init__(self,):
        """_file_directory 保存数据的目录
            _suffix 文件名后缀
            """
        self._flie_directory = sys.path[0] + '/dataFile/'
        self._suffix = '.csv'
        self.LETTERS = 'ABCDEFGHIJKLONMOPQRSTUVWXYZ'
        self.d = Queue()

    def is_exit(self):
        """csv文件是否存在"""
        for i in self.LETTERS:
            file_name = self._flie_directory + 'data' + self._suffix
            if not os.path.exists(file_name):
                with open(file_name, 'w') as f:
                    writer = csv.writer(f)
                    writer.writerow(['地区', '网址', '酒店名称', '地址', '价格', '电话','最低价格'])
                    f.close()
        return True
    def dumps(self, content):
        self.d.put(content)

    def save(self):
        """将数据存进csv文件"""
        with open(self._flie_directory+'A'+self._suffix, 'w', newline='') as w:
            writers = csv.writer(w)
            li = ('地区','网址', '酒店', '地址', '价格', '电话','最低价格')
            writers.writerow(li)
            while True:
                if self.d.empty():
                    break
                n = self.d.get()
                print(n)
                writers.writerow(n)

if __name__ == '__main__':
    data = Datafile()
    data.dumps(['北京', 'http://hotel.meituan.com/92489585/', '99优选酒店(虎坊桥地铁站店)', '西城区腊竹胡同59号（近地铁7号线虎坊桥C口）', '4.3', '010-83104641', 168.0])
    data.dumps(['12', 11])
    data.save()