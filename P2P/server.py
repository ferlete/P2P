import select, socket, sys
import threading
import numpy


class Server:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []


    def __init__(self, ip, port):
        self.server.bind((ip, port))
        self.server.listen(5)
        print("Server listen on %s:%d" % (ip, port))
        self.saveserverup(ip, port)

    def handler(self, c, a):
        while True:
                data = c.recv(1024)
                for conection in self.connections:
                        data = data [::-1]
                        conection.send(data)
                if not data:
                    print(str(a[0]) + ':' + str(a[1]) + " disconnected")
                    self.connections.remove(c)
                    c.close()
                    break

    def run(self):
        while True:
            c, a = self.server.accept()
            cThread = threading.Thread(target=self.handler, args=(c, a))
            cThread.daemon = True
            cThread.start()
            self.connections.append(c)
            print(str(a[0]) + ':' + str(a[1]) + " connected")

    def saveserverup(self, ip, port):
        with open('list_server.txt', 'a') as outfile:
            outfile.write(str(ip) + ":" + str(port) + "\n")



