#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description:
- 获取数据，加入csv文件

author:https://github.com/HANKAIluo
2018.3.18
"""

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
        file_name = self._flie_directory + 'rest' + self._suffix
        if os.path.exists(file_name):
            return True

    def open_csv(self,):
        f = open(self._flie_directory+'rest'+self._suffix, 'r',newline='')
        reader = csv.reader(f)
        url = []
        for i in reader:
            url.append(i)
        f.close()
        os.remove(self._flie_directory+'rest'+self._suffix)
        return url

    def dumps(self, content):
        self.d.put(content)

    def save(self, filename):
        """将数据存进csv文件"""
        with open(self._flie_directory+filename+self._suffix, 'a', newline='') as w:
            writers = csv.writer(w)
            #li = ('地区','网址', '酒店', '地址', '评分', '电话','最低价格')
            #writers.writerow(li)
            while True:
                if self.d.empty():
                    break
                n = self.d.get()
                print(n)
                writers.writerow(n)

if __name__ == '__main__':
    data = Datafile()
    data.is_exit()
    data.open_csv()
