import socket
from common import send, recv

def connect_to_server(ip, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.connect((ip, port))
    return server

server = connect_to_server("3.1.5.104",4000)
print(recv(server, 10))