#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
功能:创建TCP服务端
author:ompri
date:2019.04.13
'''

import socket
import threading

bind_ip="127.0.0.1"
bind_port = 8888

server=socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((bind_ip,bind_port))

#最大连接数5
server.listen(5)
print('listening on %s:%d' %(bind_ip,bind_port))

#客户端线程
def handle_client(client_socket):
    request=client_socket.recv(1024)
    print('received: %s' %(request))
    client_socket.send(b'ACK!')
    client_socket.close()

while True:
    client,addr=server.accept()     #client为客户端套接字,addr为ip和端口
    print(client,addr)
    print('accepted connection from: %s:%d' %(addr[0],addr[1]))
    client_handler=threading.Thread(target=handle_client,args=(client,))
    client_handler.start()