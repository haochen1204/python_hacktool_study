# -*- coding: utf-8 -*
# *python3*
# *author : 昊辰*

# 漏洞名称：
# 漏洞编号：
# poc作者：
# 影响应用:             
# 影响版本:
# 漏洞类型：
# 漏洞概述：
# fofa查询：

import requests
import getopt
import datetime
import sys
import threading
import os
import urllib3
import time
import queue
from colorama import init, Fore
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=False) 

lock = threading.Lock()
global result_file_path
global proxies_judge
loop_name = ''

def exploit(url):
    '''
        poc函数
        poc代码放在这里，这个函数的内容随便修改
        可以使用接口output_to_file将信息输出到文件中
        可以使用接口output将信息显示在命令行中（当print用就行）
            output需要2个参数，一个为显示的信息，一个为信息的类型（int 0 1 2 3）
                0 普通的信息
                1 攻击成功的信息
                2 攻击失败的信息
                3 出现错误的信息
    '''
    global proxies_judge
    proxies = {
    "http": 'http://127.0.0.1:8080',
    "https": 'http://127.0.0.1:8080'
    }
    head = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36'}
    exp = url
    try:
        if proxies_judge:
            re = requests.get(exp,verify=False,timeout=5,proxies=proxies)
        else:
            re = requests.get(exp,verify=False,timeout=5)
        if re.status_code == 200:
            rarsize = int(re.headers.get('Content-Length'))
            if rarsize // 1024 > 100:
                msg = "存在目录 文件大小为"+str(rarsize)+' '+exp
            else:
                msg = '存在目录，但文件较小，请手动验证 '+url 
            judge = 1
            output_to_file(msg)
        else:
            msg = '不存在目录'+url
            judge = 2
    except:
        msg = 'error! 目标路径无法访问'
        judge = 3
    output(msg,judge)

def handle(msg):
    url = queue.Queue()
    suffixFormat = ['rar', 'zip', 'gz', 'tar.gz']
    for urll in msg:
        ucp = ''
        if urll[-1] == '/':
            urll = urll[0:-1]
        if urll.startswith('http://'):
            ucp = urll.lstrip('http://')
        elif urll.startswith('https://'):
            ucp = urll.lstrip('https://')

        if '/' in ucp:
            ucp = ucp.split('/')[0]
        if ':' in ucp:
            cport = ucp.split(':')[1]
            ucp = ucp.split(':')[0]
            www1 = ucp.split('.')
        else:
            www1 = ucp.split('.')
        wwwlen = len(www1)
        wwwhost = ''
        for i in range(1, wwwlen):
            wwwhost += www1[i]
        domainDic = [ucp + '.', ucp.replace('.', '') + '.', 'wz.', 'sql.', 'wwwroot.', 'index.', 'old.', 'web.',
                    'database.', 'upload.', 'website.', 'wangzhan.',
                    'package.', 'bin.', 'ftp.', 'output.', 'config.', '网站备份.', '网站.', '数据库.', '数据库备份.', 'sjk.',
                    'shujuku.', 'home.',
                    'backup.', 'faisunzip.',
                    '1.',
                    '2.',
                    '3.',
                    '4.',
                    '5.',
                    '6.',
                    '7.',
                    '8.',
                    '9.',
                    '666.',
                    '777.',
                    '888.',
                    '999.',
                    '234.',
                    '555.',
                    '333.',
                    '444.',
                    'admin.', 'db.', 'test.', '123.', 'admin.', 'root.', 'data.', '666.',
                    '111.', 'beifen.',
                    'b.', 'template.', 'install.', 'core.', 'about.', 'cache.', 'download.',
                    'runtime.', 'a.', 'img.', 'include.',
                    '000.', '00.', '0.', '012.',
                    'application.', 'server', 'extend.', 'vendor.', 'app.', 'public.'
                                                                            'bf.', wwwhost + '.',
                    ucp.split('.', 1)[-1] + '.', www1[0] + '.', www1[1] + '.']
        for a in suffixFormat:
            for b in domainDic:
                url.put(urll+'/'+b+a)
    return url

def output_to_file(msg):
    '''
        输出到文件
    '''
    global result_file_path
    f = open(result_file_path,'a')
    f.write(msg+'\n')
    f.close()

def output(msg,judge=0):
    '''
        输出到命令行
        在多线程的情况下，输出可能会混乱，这里加了个锁来保证输出结果的稳定，但会略微影响扫描效率
        如果不想要锁，追求极致的速率（mac下不加锁也不会乱，不晓得什么原因）
        请删除
            lock.acquire()
            try:
            finally:
            lock.release()
        4行代码
    '''
    lock.acquire()
    try:
        now_time = datetime.datetime.now().strftime('%H:%M:%S')
        now_time = Fore.LIGHTBLUE_EX + '['+now_time+'] ' + Fore.RESET 
        if judge == 0:
            print(now_time + msg )
        elif judge == 1: # 输出成功信息
            print(now_time + Fore.LIGHTGREEN_EX + '[+] ' + msg + Fore.RESET)
        elif judge == 2: # 输出失败信息
            print(now_time + Fore.LIGHTYELLOW_EX + '[-] ' + msg + Fore.RESET)
        elif judge == 3: # 输出错误信息
            print(now_time + Fore.LIGHTRED_EX +'[-] ' + msg + Fore.RESET)
    finally:
        lock.release()

def help():
    '''
        帮助文档
    '''
    print("""
    -h --help                   帮助文档
    -u --url                    目标url
    -f --target_file            目标地址的文件
    -r --resutl_file            输出的信息文件地址（默认为resutl.txt）
    -t --thread_num             多线程数量（默认50）
    -p --proxies                是否开启代理,默认不开启，输入则开启，一般用于brup抓测试
eg：
    python3 poc模版.py -u http://www.xxx.com
    python3 poc模版.py -f target.txt
    python3 poc模版.py -f target.txt -r result.txt
    python3 poc模版.py -f target.txt -r result.txt -t 100
    """)

def poc_head():
    print("""

        ______  _________________________________
        ___  / / /_  ____/__  __ \_  __ \_  ____/
        __  /_/ /_  /    __  /_/ /  / / /  /     
        _  __  / / /___  _  ____// /_/ // /___   
        /_/ /_/  \____/  /_/     \____/ \____/                                   
                            author      昊辰
                            博客：      www.haochen1204.com
                            公众号：    霜刃信安
                            漏洞名称：  {}
    """.format(loop_name))

def main():
    global proxies_judge
    global result_file_path
    result_file_path = 'result.txt'
    target_num = 50
    target_file_path = ''
    url = ''
    msg = []
    proxies_judge = False

    poc_head()

    try:
        opts, args = getopt.getopt(sys.argv[1:], 
        "hf:r:t:u:p",
        ["help","target_file=","result_file=","thread_num=","url=","--proxies"])
    except getopt.GetoptError as err:
        print(str(err))
        help()

    # 从opts中读取数据，o为参数,a为参数后带的值
    for o,a in opts:
        if o in ['-h','--help']:            
            help()
        elif o in ['-u','--url']:
            msg.append(a)
        elif o in ['-f','--target_file']:            
            target_file_path = a  
            try:
                f = open(target_file_path,'r')
                msg = f.read().split('\n')
            except:
                output('目标文件路径错误！' , 3)
        elif o in ['-r','--result']:
            result_file_path = a
        elif o in ['-t',"--thread_num"]:
            target_num = int(a)
        elif o in ['-p',"--proxies"]:
            proxies_judge = True
    
    target = handle(msg)
    i = 0
    if url == '' and len(msg) != 0:
        while True:
            if threading.active_count()-1 < target_num and target.empty() == False:
                t = threading.Thread(target=exploit,args=(target.get(),))
                t.start()
                i+=1
                output_msg = '第'+str(i)+'个目标开始检查，还有'+str(target.qsize())+'个目标待检查！'
                output(output_msg)
            if target.empty() and threading.active_count() == 1:
                f = open(result_file_path,'r')
                num = len(f.readlines())
                output('finish! 共扫描'+str(len(msg))+'个网站，发现备份文件'+str(num)+'个！')
                break
            elif target.empty() and threading.active_count() > 1:
                output('正在检测最后'+str(threading.active_count()-1)+'个目标，请稍等...')
                time.sleep(5)
        os.rename(result_file_path,result_file_path+' '+str(num))
    elif url != '' and len(msg) == 0:
        exploit(url)

if __name__ == '__main__':
    main()