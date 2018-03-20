#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Description:
- 多线程，队列操作，断点续传

author:https://github.com/HANKAIluo
2018.3.18
"""

import threading
from queue import Queue
from crawl import Crawl
from datafile import Datafile
from getproxy import get_proxy
import time


Datafile = Datafile()

proxies = get_proxy()

thread_count = 40

class MasterThread:

    def __init__(self):
        self.count = {
            'count': 0,  #爬取总数
            'failed_count': 0,   #爬取失败总数
            'sucess_count': 0,   #成功爬取总数
            'start_time': time.asctime(),    #开始时间
            'end_time': 0,   #结束时间
        }
        self.endtime = time.localtime().tm_min + 1
        self.proxy = next(proxies)
        self.Crawl = Crawl()
        self.Crawl.proxy = self.proxy

        self.Taskqueue = Queue()
        self.Urlqueue = Queue()

    def send(self):
        """
        爬取市级酒店的网址并加入队列
        """
        cities = self.Crawl.get_cities_url()
        for i in cities:
            self.Taskqueue.put({i:cities[i]})
        self.count['count'] = self.Taskqueue.qsize()

    def recv(self):
        """获取所有酒店网址并加入队列"""
        if not self.Taskqueue.empty():
            n = self.Taskqueue.get()
            url = [n[i] for i in n][0]
            self.log()
            hotel_list = self.Crawl.get_hotel_list(url)
            if hotel_list == []:
                self.count['failed_count'] += 1
                self.Taskqueue.put(n)
            for t in hotel_list:
                self.Urlqueue.put(t)
            print(self.Urlqueue.qsize())

    def start(self):
        """运行"""
        if Datafile.is_exit():  #断点续传
            link = Datafile.open_csv()
            for t in link:
                self.Urlqueue.put(t[0])
        else:
            boot_threading = threading.Thread(target=self.send)
            boot_threading.start()
            boot_threading.join()

            for i in range(self.count['count']):
                t = threading.Thread(target=self.recv,)
                t.start()
                t.join()
            if self.count['failed_count'] != 0:
                for i in range(self.count['failed_count']):
                    t = threading.Thread(target=self.recv, )
                    t.start()
                    t.join()
        self.count['count'] = self.Urlqueue.qsize()
        self.count['failed_count'] = 0

        thread_list = []
        for s in range(thread_count):
            workerthread = threading.Thread(target=self.run,)
            thread_list.append(workerthread)
        for t in thread_list:
            t.start()
            t.join()
        Datafile.save('data')
        while not self.Urlqueue.empty():
            sa = [self.Urlqueue.get()]
            Datafile.dumps(sa)
        Datafile.save('rest')
        print('*******************')
        self.log()

    def run(self):
        """工作线程"""
        while Datafile.d.qsize() < 10000:
            if not self.Urlqueue.empty():
                url = self.Urlqueue.get()
                data = self.Crawl.crawl(url)
                print(data)
                print(self.Crawl.proxy)
                if data:
                    self.count['sucess_count'] += 1
                    Datafile.dumps(data)
                else:
                    self.count['failed_count'] += 1
                    self.Urlqueue.put(url)
            #Datafile.dumps(data)
            self.log()

    def log(self):
        """
        每间隔5分钟切换IP
        """
        starttime = time.localtime().tm_min
        print('爬取总数: ',self.count['sucess_count'])
        print('失败总数:',self.count['failed_count'])
        print('酒店总数', self.Urlqueue.qsize())
        print('开始时间:',self.count['start_time'])
        print('————————————————————')
        if starttime == self.endtime:
            self.Crawl.proxy = next(proxies)
            self.endtime = starttime + 60
        if self.Urlqueue.empty():
            self.count['end_time'] = time.asctime()
            print('结束时间:',self.count['end_time'])

if __name__ == '__main__':
    th = MasterThread()
    th.start()