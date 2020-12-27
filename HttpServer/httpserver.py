from sys import argv
import socket
import threading
import string
import random
# import signal

HEADER = 1024
try:
    PORT = int(argv[1])
except:
    print("[SERVER-ERROR]\n-------------------------------------\nPlease Enter a valid Port number!")
    exit()
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
# signal.signal(signal.SIGINT, shutdown)
# DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def create_file(size):
    content = ""
    for _ in range(size):
        lower_upper_alphabet = string.ascii_letters
        random_letter = random.choice(lower_upper_alphabet)
        content += random_letter
    content = f"<!DOCTYPE html><html><head><title>{str(size)} bytes</title></head><body>{content}</body></html>"
    file = open("./index.html", 'w+')
    file.write(content)


def read_file(filename):
    file = open("."+filename)
    content = file.read()
    file.close()
    return content


def send_response(connection, status, file, proto):
    response = str(
        f"{proto} {status} {proto} \r\nContent-Length: {str(len(file))}\r\nContent-Type: text/html; charset={FORMAT}\r\n\r\n")
    print(
        f"[SERVER-RESPONSE MESSAGE]\n-------------------------------------\n{response}")
    connection.sendall(response.encode(FORMAT))
    connection.sendall(file.encode(FORMAT))


def handle_client(conn, addr):
    print("[SERVER-NEW CONNECTION]\n-------------------------------------\n" +
          f"{addr} is connected.\n")
    response_status = ""
    # connected = True
    filename = ""
    request = conn.recv(HEADER).decode(FORMAT)
    headers = request.split("\n")
    req_info = headers[0].split()
    response_proto = req_info[2]
    req_method = req_info[0]
    print(
        f"\n[SERVER-REQUEST INFORMATION]\n-------------------------------------\n{request}\n")
    if req_method == "GET":
        try:
            req_file_size = req_info[1].split('/')[1]
            req_file_size = int(req_file_size)
            if req_file_size < 100 or req_file_size > 20000:
                response_status = "400 Bad Request"
                filename = "/400.html"
            else:
                response_status = "200 OK"
                filename = "/index.html"
                create_file(req_file_size)

        except:
            response_status = "400 Bad Request"
            filename = "/400.html"
    else:
        response_status = "501 Not Implemented"
        filename = "/501.html"
    file = read_file(filename)
    send_response(conn, response_status, file, response_proto)
    conn.close()
    return response_status


def start():
    server.listen(10)
    print(f"[SERVER-LISTENING] Server is listening on {SERVER}:{PORT}")
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        print(f"[SERVER-ACTIVE CONNECTIONS] {threading.activeCount() - 1}")


print("[SERVER-STARTING] server is starting...")
start()
