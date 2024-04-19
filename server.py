from enum import Enum
import hashlib
import socket
import struct
import threading
import time
import json
import sys

# import dataclass


HOST = '127.0.0.1'
PORT = 12345

BUFFER_SIZE = 2048
FILE_PATH = sys.argv[1] if len(sys.argv) > 1 else "file.pdf"
TIMEOUT = 5

server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind((HOST, PORT))



def read_chunk(file, start, size):
    file.seek(start)
    return file.read(size)

def handle_connection(data, addr):
    request = data.decode('utf-8')

    if request == "GET":
        with open(FILE_PATH, 'rb') as f:
            checksum = hashlib.md5(f.read()).digest()
        server_socket.sendto(checksum, addr)

        i = 0
        try:
            with open(FILE_PATH, 'rb') as file:
                while True:
                    chunk = read_chunk(file, i * BUFFER_SIZE, BUFFER_SIZE)
                    if not chunk:
                        print("File sent successfully")
                        break

                    # Send the chunk with sequence number
                    server_socket.sendto(struct.pack('I', i) + chunk, addr)

                    # Wait for an ACK
                    start_time = time.time()
                    while True:
                        start_time = time.time()
                        # server_socket.settimeout(TIMEOUT)
                        print("Waiting for ACK")
                        ack, address = server_socket.recvfrom(4)
                        ack = struct.unpack('I', ack)[0]
                        if ack == i:
                            print("ACK Received")
                            break 
                        if time.time() - start_time > TIMEOUT:
                            print("timeout")
                            server_socket.sendto(struct.pack('I', i) + chunk, addr)
                            print(f"Resending chunk {i}")

                    i += 1
                    time.sleep(0.02)

        except FileNotFoundError:
            server_socket.sendto(b"file not found", addr)
        finally:
            # Disable the timeout after sending all chunks
            server_socket.settimeout(None)


def run_server():
    print("Server listening on {}:{}".format(HOST, PORT))
    while True:
        data, addr = server_socket.recvfrom(BUFFER_SIZE)
        if data:
            # time.sleep(0.02)
            # threading.Thread(target=handle_connection, args=(data, addr)).start()
            handle_connection(data, addr)



    return server_socket
if __name__ == '__main__':
    # run_server()  
    threading.Thread(target=run_server).start()
    # server_socket.close()

# class Action(Enum):
#     CREATE = "create"
#     READ = "read"
#     UPDATE = "update"
#     DELETE = "delete"

# @dataclass
# class Protocol:
#     action: Action
#     resource: str
