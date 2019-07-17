#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
功能:创建TCP客户端
author:ompri
date:2019.04.12
'''

import socket

target_host = '127.0.0.1'
target_port = 8888

#创建一个socket
client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)

#连接目标
client.connect((target_host,target_port))

#发送请求，返回首页内容,b''表示bytes对象
client.send(b'ls')

#接受数据
response=client.recv(4096)
print(response)
