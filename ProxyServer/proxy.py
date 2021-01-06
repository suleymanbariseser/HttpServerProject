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


def read_cached_file(filename):
    try:
        cached_file = open(f"cache{filename}", 'r')
        content = cached_file.read()
        cached_file.close()
        return content
    except IOError:
        return None


def send_response(connection, status, file, proto):
    print("[CONNECTION] PROXY -> CLIENT")
    response = str(
        f"{proto} {status} {proto} \r\nContent-Length: {str(len(file))}\r\nContent-Type: {'text/html' if file else 'x-icon'}; charset={FORMAT}\r\n\r\n")
    print(
        f"[SERVER-RESPONSE MESSAGE]\n-------------------------------------\n{response}")
    connection.sendall(response.encode(FORMAT))
    connection.sendall(file.encode(FORMAT))


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


def save_to_cache(filename, content):
    print("[PROXY-CACHE] File is cached.")
    print(filename, content)
    file = open(f"cache{filename}", 'w')
    file.write(content)
    file.close()


def connect_server(conn, request, webserver, port, filename):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            s.connect((webserver, port))
            print(f'[CONNECTION] PROXY -> SERVER')
            new_message = request.decode(FORMAT).split('\n')[0]
            print(f"[MESSAGE] {new_message}")
        except:
            file = read_file('/404.html')
            response = str(
                f"HTTP/1.1 404 Not Found HTTP/1.1 \r\nContent-Length: {str(len(file))}\r\nContent-Type: text/html; charset={FORMAT}\r\n\r\n")
            print(f'[RESPONSE]\n404 NOT FOUND')
            conn.sendall(response.encode(FORMAT))
            conn.sendall(file.encode(FORMAT))
            s.close()
            conn.close()
            return
        s.send(request)         # send request to webserver
        while 1:
            # receive data from web server
            data = s.recv(HEADER)
            print(f'[CONNECTION] SERVER -> PROXY')
            print(f"[MESSAGE] {data}")

            if (len(data) > 0):
                # send to browser
                conn.send(data)
                content = data.decode(FORMAT)
                if "Content-Length" not in content:
                    save_to_cache(filename, content)
                else:
                    print(f"[MESSAGE-NEW] {data}")

                print(f'[CONNECTION] PROXY -> CLIENT')
            else:
                print(f'[CONNECTION] PROXY -> CLIENT')
                print(f"[MESSAGE] NULL")
                break
        s.close()
        conn.close()
        print("[CONNECTION] END")
    except:
        print('[ERROR]\nAn error is occured!!!')
        if s:
            s.close()
        if conn:
            conn.close()


def read_file(filename):
    file = open("."+filename)
    content = file.read()
    file.close()
    return content


def get_file_size(url):
    if '://' in url:
        url = url.split('://')[1]
    file_size = url.split('/')[1]
    if file_size.isnumeric():
        file_size = int(file_size)
    else:
        file_size = 0
    return file_size


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
        requested_file = temp[webserver_pos:]
    if webserver == SERVER:
        print(f"\n\n[CONNECTION] START")
        print(f'[CONNECTION] CLIENT -> PROXY')
        print(f"[MESSAGE] {first_line}")
        file_size = get_file_size(request.decode(
            FORMAT).split("\n")[0].split()[1])
        request = request.decode(FORMAT).replace(
            url, requested_file).encode(FORMAT)
        if(file_size <= 9999):
            cache_content = read_cached_file(requested_file)
            if cache_content == None:
                connect_server(conn, request, webserver, port, requested_file)
            else:
                send_response(conn, "200 OK", cache_content, "HTTP/1.1")
                conn.close()
                print("[PROXY-CACHE] File is served from PROXY.")

        else:
            file = read_file('/414.html')
            response = str(
                f"HTTP/1.1 414 Request-URI Too Long HTTP/1.1 \r\nContent-Length: {str(len(file))}\r\nContent-Type: text/html; charset={FORMAT}\r\n\r\n")
            print(f'[CONNECTION]\n{response}')
            conn.sendall(response.encode(FORMAT))
            conn.sendall(file.encode(FORMAT))
            conn.close()
            pass
    else:
        conn.close()
        pass


def start():
    server.listen()
    print(f"[PROXY-LISTENING] PROXY is listening on {PROXY}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.setDaemon(True)
        thread.start()


print("[PROXY-STARTING] PROXY is starting...")
start()
