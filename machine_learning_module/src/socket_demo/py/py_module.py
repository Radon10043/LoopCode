import socket
import time

PORT = 12012
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
address = ("127.0.0.1", PORT)
server_socket.bind(address)
while True:
    now = time.time()
    receive_data, client = server_socket.recvfrom(1024)
    data = receive_data.decode("utf-8")
    print(f"data: {data}")
    if data == "start train":
        print("start train")
        for i in range(10):
            print(f"{i} training...")
        print("train end")
        server_socket.sendto("train end".encode("utf-8"), client)
