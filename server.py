import socket
import os
import time
import threading


def set_socket_server(ip, port):
    sock = socket.socket()

    sock.bind((ip, port))

    sock.listen()
    return sock


def sock_listen(sock):
    client, addr = sock.accept()
    return client


def set_transfer_location():
    desktop = os.path.join(os.path.join(os.environ['USERPROFILE']), 'Desktop')
    share_folder = os.path.join(desktop, "Share folder")
    return share_folder


def create_folder(share_folder):
    if os.path.exists(share_folder):
        return False
    else:
        os.mkdir(share_folder)
    os.chdir(share_folder)


def list_all_files(share_folder):
    all_folders = []
    all_files = []
    for root, folders, files in os.walk(share_folder):

        for eachfold in folders:
            all_folders.append(root.replace("\\", "/") +
                               "/"+eachfold.replace("\\", "/"))

        for eachfile in files:
            all_files.append(os.path.join(root, eachfile))

    return all_folders, all_files


def send_files(client, share_folder):
    print(client)
    files = os.listdir(share_folder)
    for file in files:
        client.send(bytes(file, "utf-8"))
        response = client.recv(4).decode("utf-8")
        print(file)
        print(response)
        if response == "yes":
            client.send(bytes("ok", "utf-8"))
        else:
            client.send(bytes("ok", "utf-8"))
            print(file)
            upload(client, share_folder, file)


def upload(s, share_folder, filename):
    buffer = 1024
    s.send(bytes(filename, "utf-8"))
    s.recv(4)
    filename = os.path.join(share_folder, filename)
    file_type = os.path.isfile(filename)
    print(file_type)
    if file_type:

        with open(filename, "rb") as f:
            s.send(bytes("file //" + str(os.path.getsize(filename)), "utf-8"))

            print(s.recv(4).decode("utf-8"))
            l = f.read(1024)
            s.send(l)
            while l != b'':
                l = f.read(1024)
                s.send(l)

        f.close()

        print(s.recv(buffer).decode("utf-8"))
    else:
        s.send(bytes("folder //", "utf-8"))
        s.recv(4)
        all_folders, all_files = list_all_files(share_folder)
        s.send(bytes(str(len(all_folders)), "utf-8"))
        s.recv(4)
        for a in all_folders:
            print(a)
            a = "\"" + a + "\""
            s.send(bytes(a, "utf-8"))
            s.recv(4)

        s.send(bytes(str(len(all_files)), "utf-8"))
        s.recv(4)

        for a in all_files:
            print("went to for loop")
            s.send(bytes(a.replace("\\", "/"), "utf-8"))
            print("sent filename" + a)

            print("recieved " + s.recv(4).decode("utf-8"))

            with open(a, "rb") as f:
                s.send(bytes(str(os.path.getsize(a)), "utf-8"))
                print("sent file size")

                print("recieved " + s.recv(4).decode("utf-8"))

                l = f.read(1024)
                s.send(l)
                print("sending data")
                print("recieved " + s.recv(4).decode("utf-8"))
                print("going inside while loop")
                while l != b'':
                    print(l)
                    print("went inside while loop")
                    l = f.read(1024)
                    print("sending data")
                    s.send(l)
                    print("sent data")
                    s.recv(4)

            f.close()
            s.recv(1024)


def start_server(ip, port):
    sock = set_socket_server(ip, port)
    client = sock_listen(sock)

    client.send(bytes("working", "utf-8"))

    share_folder = set_transfer_location()
    create_folder(share_folder)
    while True:
        send_files(client, share_folder)
        time.sleep(1 / 100)


def sock_connect(ip, port):
    sock = socket.socket()
    sock.connect((ip, port))
    return sock


def text_send(s, text):
    s.send(bytes(str(text), "utf-8"))


def get_files(sock, share_folder):
    print(sock)
    files = os.listdir(share_folder)
    filename = sock.recv(1024).decode("utf-8")
    print(filename)
    if filename in files:
        sock.send(bytes("yes", "utf-8"))
        sock.recv(4)
        print(filename + "exists and will not be transfered")
    else:
        sock.send(bytes("no", "utf-8"))
        sock.recv(4)

        print(filename + "does not exist and will be transfered")
        download(sock, share_folder)


def download(s, share_folder):
    name = s.recv(1024).decode("utf-8")
    name = os.path.join(share_folder, name)
    s.send(bytes("ok", "utf-8"))
    d_typa_file = s.recv(32).decode("utf-8")
    print(d_typa_file)

    if d_typa_file.startswith("file //"):
        s.send(bytes("ok", "utf-8"))
        filesize = int(d_typa_file.replace("file //", ""))
        with open(name, "wb") as f:

            data = s.recv(4096)
            totalr = len(data)
            f.write(data)
            while totalr < filesize:
                data = s.recv(4096)
                totalr += len(data)
                f.write(data)
                print("downloading")

        f.close()

        s.send(bytes("File downloaded: " +
                     name, "utf-8"))

    elif d_typa_file.startswith("folder //"):
        print("---- Starting to create folders ----- ")
        text_send(s, "ok")

        length_of_fold = s.recv(1024)

        text_send(s, "ok")
        os.system("mkdir " + name.replace(" ", "\ "))
        print("mkdir " + name)
        for a in range(0, int(length_of_fold)):

            foldername = s.recv(1024).decode("utf-8")
            print(os.system("mkdir " + foldername))
            os.system("mkdir " + foldername.replace(" ", "\ "))
            text_send(s, "ok")

        print("---- Starting to recieve files -----")
        length_of_files = s.recv(1024).decode("utf-8")
        print("recieved number of files" + str(length_of_files))

        text_send(s, "ok")
        print("Sent ok")
        for a in range(0, int(length_of_files)):

            filename = s.recv(1024).decode("utf-8")
            print("Recieved filename as " + str(filename))
            text_send(s, "ok")
            print("Sent ok")

            filesize = s.recv(1024)
            filesize = filesize.decode("utf-8")
            print("recieved file size" + filesize)

            text_send(s, "ok")
            print("Sent ok")

            filesize = int(filesize)

            with open(filename, "wb") as f:

                data = s.recv(4096)

                text_send(s, "ok")

                totalr = len(data)
                f.write(data)

                while totalr < filesize:

                    data = s.recv(4096)

                    text_send(s, "ok")

                    totalr += len(data)
                    f.write(data)

            f.close()
            s.send(bytes("File downloaded: " +
                         name, "utf-8"))


def start_client(ip, port):

    sock = sock_connect(ip, port)
    print(sock.recv(1024).decode("utf-8"))

    share_folder = set_transfer_location()

    create_folder(share_folder)

    while True:
        get_files(sock, share_folder)
        time.sleep(1 / 100)


threading.Thread(target=start_server, args=["0.0.0.0", 55664]).start()
threading.Thread(target=start_client, args=["3.1.5.105", 55665]).start()





