import socket
import sys


class Client:

    BUFFER_SIZE = 1024

    def __init__(self, ip, port):
        try:
            # Create a TCP/IP socket
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # Connect the socket to the port where the server is listening
            server_address = (ip, port)
            print('connecting to %s:%s' % server_address)
            self.s.connect(server_address)

            self.sendmessage("GET FILE")

            self.s.close()

        except Exception as e:
            print(e)
        sys.exit()

    def sendmessage(self, message):
        # Send data
        print('sending "%s"' % message)
        self.s.send(message.encode())
        data = self.s.recv(self.BUFFER_SIZE)
        print("Data: %s" % data)



