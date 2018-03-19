import sys
import requests, csv
from bs4 import BeautifulSoup

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/56.0.2924.87 Safari/537.36',}
data_file = sys.path[0]

def get_proxy_ip():
    """获取代理的网址"""
    url = 'http://www.xicidaili.com/wn/'
    pro_data = data_file + '/dataFile/proxy.csv'
    proxy_url_list = [ url + str(1) for y in range(1,3)]
    for j in proxy_url_list:
        reponse = requests.get(j, headers=headers)
        if reponse.status_code :
            html = BeautifulSoup(reponse.text,'lxml')
            ip = [t.find_next().find_next_sibling() for t in html.findAll('tr') if t != html.findAll('tr')[0]]
            port = [t.find_next().find_next_sibling().find_next_sibling() for t in html.findAll('tr') if
                    t != html.findAll('tr')[0]]
            with open(pro_data, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                new_proxies = []
                for i in range(len(ip)):
                    new_list = [ip[i].get_text(), port[i].get_text()]
                    new_proxies.append(ip[i].get_text() + ':' + port[i].get_text())
                writer.writerow(new_proxies)
                csvfile.close()
    return pro_data

def test_proxy(csvname):
    """测试代理是否有效"""
    url = 'http://httpbin.org/ip'
    useful = data_file + '/dataFile/usefulproxy.csv'
    with open(csvname, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        all_proxy = []
        all_proxy.append('117.121.33.41:80')
        all_proxy.append('123.55.1.53:34074')
        all_proxy.append('1.194.143.27:30690')
        for i in reader:
            all_proxy += i
        print(all_proxy)
        f =  open(useful, 'w', newline='',encoding='utf-8')
        writer = csv.writer(f)
        for j in all_proxy:
            proxies = {'https:': 'http://' + j}
            print(proxies)
            try:
                re = requests.get(url, proxies=proxies)
            except:
                print('error')
                continue
            writer.writerow([j])
        f.close()

def get_proxy():
    """调用一次返回一个代理"""
    _file = open(data_file+'/dataFile/usefulproxy.csv', 'r')
    rea = csv.reader(_file)
    for i in rea:
        proxy = {'https':'http://' + i[0]}
        yield proxy

if __name__ == '__main__':
    n = get_proxy_ip()
    test_proxy(n)
