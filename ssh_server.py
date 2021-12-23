import socket
import paramiko
import threading
import sys

from paramiko import server
from paramiko import common

host_key = paramiko.RSAKey(filename='test_rsa.key')

class Server(paramiko.ServerInterface):
    def __init__(self):
        self.event = threading.Event()
    def check_channel_reequest(self,kind,chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED
    def check_auth_password(self,username,password):
        if (username == 'haochen') and (password == '617465'):
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

server = sys.argv[1]
ssh_port = int(sys.argv[2])
try:
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    sock.bind((server,ssh_port))
    sock.listen(100)
    print("[+] 正在等待连接.....")
    client,addr = sock.accept()
except Exception as e:
    print("[-] error! " + str(e))
    sys.exit(1)
print("[+] 发现一个连接请求！")

try:
    bhSession = paramiko.Transport(client)
    bhSession.add_server_key(host_key)
    server = Server()
    try:
        bhSession.start_server(server=server)
    except paramiko.SSHException as x:
        print('[-] SSH negotiation failed!')
    chan = bhSession.accept(20)
    print("[+] Authenticated!")
    print(chan.recv(1024))
    chan.send("welcome to ssh!")
    while True:
        try:
            command = input("Rnter command:").strip("\n")
            if command != 'exit':
                chan.send(command)
                print(str(chan.recv(1024))+'\n')
            else:
                chan.send('exit')
                print("exiting")
                bhSession.close()
                raise Exception('exit')
        except KeyboardInterrupt:
            bhSession.close()
except Exception as e:
    print('[-] Caught exception:' + str(e))
    try:
        bhSession.close()
    except:
        pass
    sys.exit(1)


