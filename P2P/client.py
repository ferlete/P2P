import socket
import sys


class Client:
    # Create a TCP/IP socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self, ip, port):
        # Connect the socket to the port where the server is listening
        server_address = (ip, port)
        print('connecting to %s port %s' % server_address)
        self.client.connect(server_address)

    def sendmessage(self, message):

        try:
            # Send data
            print('sending "%s"' % message)
            self.client.send(message.encode())

            # Look for the response
            amount_received = 0
            amount_expected = len(message)

            while amount_received < amount_expected:
                data = self.client.recv(1024)
                amount_received += len(data)
                print('received "%s"' % data.decode())

        finally:
            print('closing socket')
            self.client.close()
