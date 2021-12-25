import queue
import threading
import os
import sys
import urllib3
import requests
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

threads = 10

target = sys.argv[1]
directory = sys.argv[2]
filters = [".jpg",".gif",".png",".css"]

# 记录当前工作路径
now_work = os.getcwd()
# 切换工作路径
os.chdir(directory)
# 创建一个队列
web_paths = queue.Queue()

for r,d,f in os.walk("."):
    for files in f:
        remote_path = "{}/{}".format(r,files)
        if remote_path.startswith("."):
            remote_path = remote_path[1:]
        if os.path.splitext(files)[1] not in filters:
            web_paths.put(remote_path)

result = []

def test_remote():
    while not web_paths.empty():
        path = web_paths.get()
        url = "{}{}".format(target,path)
        #print(url)
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64)'
        }
        
        try:
            response = requests.get(url,headers=headers)
            if response.status_code == 200:
                print("[{}] => {}".format(response.status_code,url))
                result.append(url)
            else:
                print("[-] {} 状态吗为:{}".format(url,response.status_code))
        except:
            print("[-] {} {}".format(url,"连接失败"))
            pass

for i in range(threads):
    t = threading.Thread(target=test_remote)
    t.start()

while True:
    if threading.active_count() == 1:
        os.chdir(now_work)
        f = open('result.txt','w')
        for i in result:
            f.write(i+'\n')
        f.close()
        break