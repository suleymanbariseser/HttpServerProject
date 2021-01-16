import socket

HEADER = 64
BUFFER = 32768
PORT = 5000
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = "192.168.1.102"
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)
print(f"Successfully Connected to server: {SERVER}")


def send(msg):
    message = msg.encode(FORMAT)
    #msg_length = len(message)
    #send_length = str(msg_length).encode(FORMAT)
    #send_length += b' ' * (HEADER - len(send_length))
    # client.send(send_length)
    client.send(message)
    a = client.recv(BUFFER).decode(FORMAT)
    print(f"------------------------------\n{a}")


send("PUT /2000 HTTP/1.0")
