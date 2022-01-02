import threading
import queue
import urllib
import requests
import sys

threads = 50
target_url = sys.argv[1]
wordlist_file = sys.argv[2]
resume = None
header = {
    'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:92.0) Gecko/20100101 Firefox/92.0'
}
code_list = [200,301,302]

def build_wordlist(wordlist_file):
    '''
        文件读取函数
    '''
    # 打开文件
    fd = open(wordlist_file,"r",encoding="gbk")
    # 按行读取
    raw_words = fd.readlines()
    fd.close()

    found_resume = False
    words = queue.Queue()

    for word in raw_words:
        # 删除末尾置顶空行如\r\n等
        word = word.rstrip()
        if resume is not None:
            if found_resume:
                words.put(word)
            else:
                if word == resume:
                    found_resume = True
                    print("Resuming wordlist from : {} ".format(resume))
        else:
            words.put(word)
    return words

def dir_bruter(word_queue,extensions=None):
    '''
        网站目录扫描
    '''
    while not word_queue.empty():
        attempt = word_queue.get()
        attempt_list = []

        # 如果字典中的数据是以/开头，则去除开头的/
        if attempt[0] == '/':
            attempt = attempt[1:]

        # 判断是目录还是文件
        if "." not in attempt:
            attempt_list.append("/{}/".format(attempt))
        else:
            attempt_list.append("/{}".format(attempt))

        # 如果没有后缀则添加后缀
        if extensions and "." not in attempt:
            for extension in extensions:
                attempt_list.append("/{}{}".format(attempt,extension))

        for brute in attempt_list:
            url = "{}{}".format(target_url,brute)
            try:
                r = requests.get(url,headers=header)
                if len(r.text) and r.status_code in code_list:
                    print("[{}] => {}".format(r.status_code,url))
            except:
                pass

word_queue = build_wordlist(wordlist_file)
extensions = [".php",".bak",".orig",".inc","jsp"]

for i in range(threads):
    t = threading.Thread(target=dir_bruter,args=(word_queue,extensions))
    t.start()
