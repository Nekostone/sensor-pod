import os
from socket import *
from struct import unpack
import json

class ServerProtocol:

    def __init__(self):
        self.socket = None
        self.output_dir = '.'
        self.file_num = 1

    def listen(self, server_ip, server_port):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.bind((server_ip, server_port))
        self.socket.listen(1)

    def handle_data(self):
        try:
            while True:
                (connection, addr) = self.socket.accept()
                try:
                    bs = connection.recv(8)
                    (length,) = unpack('>Q', bs)
                    data = b''
                    while len(data) < length:
                        to_read = length - len(data)
                        received_data = connection.recv(
                            4096 if to_read > 4096 else to_read)
                        data += received_data

                    # send our 0 ack
                    assert len(b'\00') == 1
                    connection.sendall(b'\00')
                finally:
                    connection.shutdown(SHUT_WR)
                    connection.close()

                decoded_data = data.decode("utf-8")
                received_json = json.loads(decoded_data)
                print("received_json: {0}".format(received_json))
                print("type(received_json): {0}".format(type(received_json)))

                self.file_num += 1
        finally:
            print("closing port...")
            self.close()

    def close(self):
        self.socket.close()
        self.socket = None

        # could handle a bad ack here, but we'll assume it's fine.

if __name__ == '__main__':
    sp = ServerProtocol()
    sp.listen('0.0.0.0', 9999)
    sp.handle_data()
