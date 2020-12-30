import socket
import threading
import time

HEADER = 4096
PORT = 8888
PROXY = "127.0.0.1"
SERVER = socket.gethostbyname(socket.gethostname())
# SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (PROXY, PORT)
FORMAT = 'utf-8'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def get_server_response(new_socket):
    connected = True
    while connected:
        try:
            data = new_socket.recv(HEADER)
            print(data)
            connected = True
        except:
            print("Error")

    pass


def connect_server(conn, request, webserver, port):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((webserver, port))
        s.send(request)         # send request to webserver
        while 1:
            # receive data from web server
            data = s.recv(HEADER)
            if (len(data) > 0):
                # send to browser
                conn.send(data)
            else:
                break
        s.close()
        conn.close()
    except:
        print('[ERROR] LINE-47')
        if s:
            s.close()
        if conn:
            conn.close()


def handle_client(conn, addr):
    request = conn.recv(HEADER)
    # parse the first line
    first_line = request.decode(FORMAT).split('\n')[0]

    # get url
    url = first_line.split(' ')[1]
    http_pos = url.find("://")  # find pos of ://
    if (http_pos == -1):
        temp = url
    else:
        temp = url[(http_pos+3):]  # get the rest of url

    port_pos = temp.find(":")  # find the port pos (if any)

    # find end of web server
    webserver_pos = temp.find("/")
    if webserver_pos == -1:
        webserver_pos = len(temp)

    webserver = ""
    port = -1
    if (port_pos == -1 or webserver_pos < port_pos):

        # default port
        port = 80
        webserver = temp[:webserver_pos]

    else:  # specific port
        port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        webserver = temp[:port_pos]
    # server_name, server_port = url.split(':')
    # server_port = int(server_port)
    if webserver == SERVER:
        connect_server(conn, request, webserver, port)
        print('[LINE-90] FINISHED')
    else:
        print('[LINE-92] TEST')
        pass


def start():
    server.listen()
    print(f"[PROXY-LISTENING] PROXY is listening on {PROXY}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.setDaemon(True)
        thread.start()
        print(f"[PROXY-ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[PROXY-STARTING] PROXY is starting...")
start()
