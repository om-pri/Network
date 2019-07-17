#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
功能:创建TCP客户端
author:ompri
date:2019.04.12
'''

import socket

target_host="127.0.0.1"
target_port=9999

#创建一个socket
client=socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

#发送数据
client.sendto(b"AAABBBCCC",(target_host,target_port))

#接受数据
data,addr=client.recvfrom(4096)

print(data)
print(addr)