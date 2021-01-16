"""
    CSE 4074 - Computer Networks - Project
    150116055 - Suleyman Barış Eser
    150115025 - Mert İsmail Eği

"""


from sys import argv
import socket
import threading
import string
import random

HEADER = 24576
try:
    PORT = int(argv[1]) #check if a port number is entered or not 
except: # port number not entered then exit code
    print("[SERVER-ERROR]\n-------------------------------------\nPlease Enter a valid Port number!")
    exit()
SERVER = socket.gethostbyname(socket.gethostname()) #get local ip address
ADDR = (SERVER, PORT) # concatenate ip address and port number
FORMAT = 'utf-8' # text format
httpserver = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #create a socket
httpserver.bind(ADDR)   # connect socket to given address


def create_file(size): #creates a random file which contains "size" bytes word
    content = ""
    for _ in range(size):
        lower_upper_alphabet = string.ascii_letters
        random_letter = random.choice(lower_upper_alphabet)
        content += random_letter # add random letter to content
    content = f"<!DOCTYPE html><html><head><title>{str(size)} bytes</title></head><body>{content}</body></html>" # convert it to html file
    return content


def send_response(connection, status, file, proto):
    response = str(
        f"{proto} {status} {proto} \r\nContent-Length: {str(len(file))}\r\nContent-Type: {'text/html' if file else 'x-icon'}; charset={FORMAT}\r\n\r\n")
    print(
        f"[SERVER-RESPONSE MESSAGE]\n-------------------------------------\n{response}")
    connection.sendall(response.encode(FORMAT)) #encode response line and send it to client
    connection.sendall(file.encode(FORMAT)) # encode file content and send it to client
    # we can send them with one response but in proxy i handle file and store it to cache. So it will be better to use like that

def get_file_size(url):
    if '://' in url:
        url = url.split('://')[1]
    file_size = url.split('/')[1]
    if file_size.isnumeric(): # if it is numeric than parse it to integer and return
        file_size = int(file_size) 
    else:
        file_size = 0
    return file_size


def handle_client(conn, addr):
    print("[SERVER-NEW CONNECTION]\n-------------------------------------\n" +
          f"{addr} is connected.\n")
    response_status = ""
    request = conn.recv(HEADER).decode(FORMAT) # decode it 
    headers = request.split("\n")
    req_info = headers[0].split() # GET /500 HTTP/1.0
    method = req_info[0]     # GET
    url = req_info[1]   # /500
    proto = req_info[2] # HTTP/1.0
    print(req_info)
    print(
        f"\n[SERVER-REQUEST INFORMATION]\n-------------------------------------\n{request}\n")
    content = ""
    if method == "GET": # we handle only get method
        try:
            file_size = get_file_size(url) # get file size
            if url == '/favicon.ico': # if requested file is favico then return 200 OK. We do not handle this file
                response_status = "200 OK"
            elif 100 <= file_size <= 20000: # if requested file is OK.
                response_status = "200 OK"
                content = create_file(file_size) # create the file
            else:
                response_status = "400 Bad Request"
        except:
            response_status = "400 Bad Request"
    else:
        response_status = "501 Not Implemented"
    print("File Size=", str(len(content)))
    send_response(conn, response_status, content, proto) # create reponse and send it to client
    conn.close()


def start():
    httpserver.listen(10) # listen requests for 10 interval time 
    print(f"[SERVER-LISTENING] Server is listening on {SERVER}:{PORT}")
    while True:
        conn, addr = httpserver.accept()    #accept client
        thread = threading.Thread(target=handle_client, args=(conn, addr)) # assign a thread for client
        thread.start() # start thread
        print(f"[SERVER-ACTIVE CONNECTIONS] {threading.activeCount() - 1}")
    httpserver.close() # close server


print("[SERVER-STARTING] server is starting...")
start()
