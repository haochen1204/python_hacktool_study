import imp
import requests
import sys
import getopt
from bs4 import BeautifulSoup
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

target_url = ''
target = []

def scan(url):
    global target

    head = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:94.0) Gecko/20100101 Firefox/94.0',
    'Accept-Encoding':'gzip, deflate, kaipule',
    'Connection':'close'}
    proxies={
    "http":"http://127.0.0.1:7777",
    "https" :"http://127.0.0.1:7777"
    }
    try:
        re = requests.get(url,headers=head,proxies=proxies,verify=False)
        bs = BeautifulSoup(re.text,'html.parser')
        for j in bs.find_all('a'):
            if target_url in j['href']:
                if j['href'] not in target:
                    target.append(j['href'])
                    print(j['href'])
                    f = open('resut.txt','a')
                    f.write(j['href']+'\n')
                    f.close()
    except Exception as e:
        print('error!'+ str(e))

def main():
    global target_url
    global target

    try:
        opts,args = getopt.getopt(sys.argv[1:],
        'u:',
        ['url='])
    except:
        print('请输入正确的参数')
    
    for o,a in opts:
        if o in ['-u','--url']:
            target_url = a
            target.append(target_url)

    for i in target:
        scan(i)

main()