# import socket programming library
import socket

# import thread module
import threading

import sys


class Server:
    #port = 9999
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []

    def __init__(self, port):
        self.sock.bind(('0.0.0.0', port))
        self.sock.listen(5)
        print("Server listen on %s" % port)

    def handler(self, c, a):
        while True:
                data = c.recv(1024)
                for conection in self.connections:
                        conection.send(data)
                if not data:
                    print(str(a[0]) + ':' + str(a[1]) + " disconnected")
                    self.connections.remove(c)
                    c.close()
                    break

    def run(self):
        while True:
            c, a = self.sock.accept()
            cThread = threading.Thread(target=self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            print(str(a[0]) + ':' + str(a[1]) + " connected")
