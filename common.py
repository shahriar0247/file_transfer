def send(sock, text):
    sock.send(bytes(text, "utf-8"))

def recv(sock, buffer):
    recieved = sock.recv(buffer)
    total = b''
    while recieved != b'':
        total = total + recieved
        recieved = sock.recv(buffer)
    return total

def decode(data):
    data = data.decode("utf-8")
    return data