# -*- coding: utf-8 -*-
import random
import socket
import time

# client 发送端
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
PORT = 12012

while True:
    start = time.time()  # 获取当前时间
    print(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(start)))  # 以指定格式显示当前时间
    msg = "test\t" + time.time().__str__()  # 发送的数据
    server_address = ("127.0.0.1", PORT)  # 接收方 服务器的ip地址和端口号
    client_socket.sendto(msg.encode(), server_address)  # 将msg内容发送给指定接收方
    time.sleep(1)  # 休眠1秒
