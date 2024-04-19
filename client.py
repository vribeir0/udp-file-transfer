import socket
import struct
import time
import json

import hashlib

HOST = '127.0.0.1'
PORT = 12345

OUTPUT_PDF = 'received/pdf.pdf'

BUFFER_SIZE = 2060

client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def validate_checksum(received_checksum, filename):
    with open(filename, 'rb') as f:
        calculated_checksum = hashlib.md5(f.read()).digest()
    return received_checksum == calculated_checksum

def send_request():
    client_socket.sendto("GET".encode('utf-8'), (HOST, PORT))
    checksum_data, _ = client_socket.recvfrom(16)  # MD5 checksums are 16 bytes
    received_checksum = checksum_data
    try:
        with open(OUTPUT_PDF, 'wb') as file:
            expected_sequence_number = 0
            
            client_socket.settimeout(5)
            while True:
                data, addr = client_socket.recvfrom(2086)
                if not data:
                    print("File received")
                    break

                received_sequence_number, chunk = struct.unpack('I', data[:4]), data[4:]

                if received_sequence_number[0] == expected_sequence_number and chunk:
                    # # Teste de arquivo sendo recebido
                    # client_socket.settimeout(2)
                    # compare_file = open("pdf menor.zip", "rb")
                    # compare_file.seek(received_sequence_number[0] * 2048)
                    # tchunk = compare_file.read(2048)
                    # if tchunk != chunk:
                    #     print("Chunks are not equal, comparing bytes...")
                    #     for i, (byte_tchunk, byte_chunk) in enumerate(zip(tchunk, chunk)):
                    #         if byte_tchunk != byte_chunk:
                    #             print(f"Difference at byte {i}: tchunk={byte_tchunk}, chunk={byte_chunk}")
                    #     print("retransmit")
                    #     continue

                    file.write(chunk)
                    print(f"sending ack {received_sequence_number[0]}")
                    client_socket.sendto(struct.pack('I', received_sequence_number[0]), addr)
                    expected_sequence_number += 1                 
    except socket.timeout:
        if validate_checksum(received_checksum, OUTPUT_PDF):
            print("File received correctly")
        else:
            print("File received with errors")

if __name__ == '__main__':

    send_request()