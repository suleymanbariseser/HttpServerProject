import socket
import threading
import time
from os import path

HEADER = 24576
PORT = 8888 # proxy will run on 8888th port
PROXY = "127.0.0.1" # proxy address which is setted on proxy settings of OS
SERVER = socket.gethostbyname(socket.gethostname()) # local ip address. It will be used for filtering requests
ADDR = (PROXY, PORT)
FORMAT = 'utf-8'
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create socket
server.bind(ADDR)


def read_cached_file(filename, file_size):
    try:
        cached_file = open(f"cache{filename}", 'r') #open file 
        content = cached_file.read()    # read 
        cached_file.close() # close
        """
            if there is a thread which writes a content on file and there is another one which try to read then,
            this condition check does not give permission to thread which try to read it.
        """
        if file_size == len(content) - 79:
            return content
        else:
            return None
    except IOError:
        print("AN ERROR OCCURED")
        return None


def send_response(connection, status, file, proto):
    print("[CONNECTION] PROXY -> CLIENT")
    response = str(
        f"{proto} {status} {proto} \r\nContent-Length: {str(len(file))}\r\nContent-Type: {'text/html' if file else 'x-icon'}; charset={FORMAT}\r\n\r\n")
    print(
        f"[SERVER-RESPONSE MESSAGE]\n-------------------------------------\n{response}")
    connection.sendall(response.encode(FORMAT))  # same method. it already descibed on server
    connection.sendall(file.encode(FORMAT))

def save_to_cache(filename, content): # write content to a file which is named with filename parameter
    print("[PROXY-CACHE] File is cached.")
    file = open(f"cache{filename}", 'w') 
    file.write(content)
    file.close()


def connect_server(conn, request, webserver, port, filename):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket for server
        """
            this try-except block try to connect the server. While trying connect if a timeout occurs then,
            we can say there is no such kind of process and return 404 Not Found Error.
        """
        try:
            s.connect((webserver, port)) # connect server
            print(f'[CONNECTION] PROXY -> SERVER')
        except:
            response = str(
                f"HTTP/1.1 404 Not Found HTTP/1.1 \r\nContent-Length: 0\r\nContent-Type: text/html; charset={FORMAT}\r\n\r\n")
            print(f'[RESPONSE]\n404 NOT FOUND')
            conn.sendall(response.encode(FORMAT)) # send client 404 error
            s.close() #close connection for server
            conn.close() # close connection for client
            return
        s.send(request)         # send request to webserver
        while 1: #wait for response
            # receive data from web server
            data = s.recv(HEADER)
            if (len(data) > 0): # if data is not null
                # send to browser
                conn.send(data)
                content = data.decode(FORMAT) # decode data
                """
                    This is same condition which we described in read_cached_file function.
                    If already a procces start to write to cache then, do not give permission to
                    other processes which try to write
                """
                if "Content-Length" not in content and not path.exists(f"cache{filename}"):
                    save_to_cache(filename, content) # content is saved to cache
            else:
                break
        s.close() # close connection for server
        conn.close() # close connection for client
        print("[CONNECTION] END")
    except: # if there is an error then close connections
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
        if(file_size <= 9999): # if requested file is smaller than 10000 then proxy can do operation
            cache_content = read_cached_file(requested_file, file_size) # if file is already in cache
            if cache_content == None: # if not in cache
                connect_server(conn, request, webserver, port, requested_file) # connect http server
            else:
                send_response(conn, "200 OK", cache_content, "HTTP/1.1") # send response from proxy to client
                conn.close() #  close connection
                print("[PROXY-CACHE] File is served from PROXY.")

        else:
            response = str(
                f"HTTP/1.1 414 Request-URI Too Long HTTP/1.1 \r\nContent-Length: 0\r\nContent-Type: text/html; charset={FORMAT}\r\n\r\n")
            print(f'[CONNECTION]\n{response}')
            conn.sendall(response.encode(FORMAT)) #if file is greater than and equal to 10000 then return 414 Request-URI Too Long Error
            conn.close() # close connection
            pass
    else:
        conn.close() 
        pass


def start():
    server.listen(10)
    print(f"[PROXY-LISTENING] PROXY is listening on {PROXY}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.setDaemon(True)
        thread.start()


print("[PROXY-STARTING] PROXY is starting...")
start()
