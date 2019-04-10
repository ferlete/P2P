import socket
import sys
import threading
import os


class Client:

    BUFFER_SIZE = 1024
    REQUEST_STRING = "GET FILE"

    def __init__(self, ip, port, filename, slice):
        self.slice = slice
        try:
            # Create a TCP/IP socket
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # allow python to use recently closed socket
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Connect the socket to the port where the server is listening
            server_address = (ip, port)
            print('[+] connecting to %s:%s' % server_address)
            self.socket.connect(server_address)

            # create to work on a different thread
            i_thread = threading.Thread(target=self.retr_file, args=(filename, self.socket))
            i_thread.daemon = False
            i_thread.start()

        except Exception as e:
            print(e)
        sys.exit()

    def retr_file(self, filename, socket):
        try:
            print("[+] resquest filename %s" % filename)
            socket.send(filename.encode())
            data = socket.recv(self.BUFFER_SIZE)
            #print(data)
            if data[:6].decode() == 'EXISTS':
                cwd = os.getcwd()
                path_to_newfile = cwd + "/music/slice_" + str(self.slice) + "_" + filename.strip()

                socket.send(("SLICE"+str(self.slice)).encode())
                data = socket.recv(self.BUFFER_SIZE)
                #print(data)

                slicesize = int(data[3:])
                print("slicesize: %d" % slicesize)
                if slicesize == 0:
                    print("[-] slice not found in server")
                    data = socket.recv(self.BUFFER_SIZE)
                else:
                    f = open(path_to_newfile, 'wb')
                    data = socket.recv(self.BUFFER_SIZE)
                    totalRecv = len(data)
                    f.write(data)
                    while totalRecv < slicesize:
                        data = socket.recv(self.BUFFER_SIZE)
                        totalRecv += len(data)
                        f.write(data)
                        #print("{0:.2f}".format((totalRecv/float(slicesize))*100)+"% Done")
                    print("[+] Download Complete!")
            else:
                print("[-] File does not Exists")
            socket.close()

        except KeyboardInterrupt as e:
            # If a user turns the server off due to KeyboardInterrupt
            self.s.close()
            return