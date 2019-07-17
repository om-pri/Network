#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
功能:创建proxy，相当于burp
测试:
author:ompri
date:2019.06.24
'''

import sys
import socket
import threading

def server_loop(local_host, local_port, remote_host, remote_port, receive_first):

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        server.bind((local_host, local_port))  #监听本地端口，等待连接
    except:
        print("Failed to listen on %s:%d" % (local_host, local_port))
        print("Check for other listening sockets or correct permissions")
        sys.exit(0)
    print("Listening on %s:%d" % (local_host, local_port))

    server.listen(5)

    while True:
        client_socket, addr = server.accept()

        #打印出本地连接信息
        print("Received incoming connection from %s:%d" % (addr[0], addr[1]))

        #开启一个线程与远程主机通信
        proxy_thread = threading.Thread(target=proxy_handler, args=(client_socket, remote_host, remote_port, receive_first))

        proxy_thread.start()

def main():
    #if len(sys.argv[1:]) != 5:
    #    print("Usage: ./proxy.py [localhost] [localport] [remotehost] [remoteport] [receive_first]")
    #    print("Example: ./proxy.py 127.0.0.1 80 www.baidu.com 80 True")
    #    sys.exit(0)

    #设置本地监听
    #local_host = sys.argv[1]
    #local_port = int(sys.argv[2])
    local_host = '127.0.0.1'
    local_port = 8080

    # 设置远程目标
    #remote_host = sys.argv[3]
    #remote_port = int(sys.argv[4])
    remote_host = 'www.baidu.com'
    remote_port = 80

    #告诉代理在发送数据给远程主机之前，是否先连接远程主机和接受远程主机发过来的数据
    #receive_first = sys.argv[5]
    #if "True" in receive_first:
    #    receive_first = True
    #else:
    #    receive_first = False
    receive_first = False

    server_loop(local_host, local_port, remote_host, remote_port, receive_first)

def proxy_handler(client_socket, remote_host, remote_port, receive_first):
    
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    remote_socket.connect((remote_host, remote_port))

    #如果receive_first为True，那么，我们先从远程主机接收数据
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        # 发送给我们的响应处理
        remote_buffer = response_handler(remote_buffer)

        #如果我们有数据发送个本地客户端，发送它
        if len(remote_buffer):
            print("Sending %d bytes to localhost." % len(remote_buffer))
            client_socket.send(remote_buffer)

    #现在我们从本地循环读取数据，发给远程主机和本地主机
    while True:
        local_buffer = receive_from(client_socket)

        if len(local_buffer):
            print("Received %d bytes from localhost." % len(local_buffer))
            hexdump(local_buffer)

            #发送给我们的本地请求
            local_buffer = request_handler(local_buffer)

            #向远程主机发送数据
            remote_socket.send(local_buffer)
            print("Send to remote")

        #接受响应数据
        remote_buffer = receive_from(remote_socket)

        if len(remote_buffer):
            print("Received %d bytes from remote host." % len(remote_buffer))
            hexdump(remote_buffer)

            # 发送到响应处理程序
            remote_buffer = response_handler(remote_buffer)

            # 将响应发给本地socket
            client_socket.send(remote_buffer)
            print("Send to localhost")

        if not len(local_buffer) or not len(remote_buffer):
            client_socket.close()
            remote_socket.close()
            print("No more data. Closing connections.\n")
            break

def hexdump(src, length=16):
    result = []
    digits = 4 if isinstance(src, unicode) else 2

    for i in range(0, len(src), length):
        s = src[i:i+length]
        hexa = b' '.join(["%0*X" % (digits, ord(x)) for x in s])
        print(hexa)
        text = b''.join([x if 0x20 <= ord(x) < 0x7F else b'.' for x in s])
        result.append(b"%04X    %-*s    %s" % (i, length*(digits + 1), hexa, text))
        print(b'\n'.join(result))

def receive_from(connection):
    buffer = ""

    #我们设置了两秒超时，这取决与目标的情况，可能需要调整
    connection.settimeout(2)

    try:
        while True:
            data = connection.revc(4096)
            if not data:
                break
            buffer += data
    except:
        pass

    return buffer

def request_handler(buffer):
    return buffer
def response_handler(buffer):
    return buffer

main()