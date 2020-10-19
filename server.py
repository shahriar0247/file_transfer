import socket
from common import send, recv

def create_socket(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))
    sock.listen(5) # become a server socket, maximum 5 connections
    return sock

def accept_client(sock):
    client, address = sock.accept()
    return client, address

sock = create_socket("0.0.0.0", 4000)
client, address = accept_client(sock)
send(client, "hellsadsssssssssssasdasdjsakhdsa kdjhsakjdhsajkd hsakjdhsajkd hsakdjhsakdjahsdkljsa hdkjsahdsssssssssssssso")
