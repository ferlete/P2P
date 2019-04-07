import select, socket, sys
import threading
import numpy


class Server:
    connections = []
    msg = ""
    protocol = 'TCP'
    REQUEST_STRING = "GET FILE"
    BUFFER_SIZE = 1024

    def __init__(self, ip, port, protocol, msg):
        try:
            self.msg = msg
            self.protocol = protocol

            if self.protocol == 'TCP':
                # define a socket TCP
                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            if self.protocol == 'UDP':
                # define a socket UDP
                self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            self.connections = []

            # make a list of peers
            self.peers = []

            # bind the socket
            self.s.bind((ip, port))

            if self.protocol == 'TCP':
                # listen for connection
                self.s.listen(1)

            print("[*] Server listen on %s %s:%d" % (protocol, ip, port))

            # save peer server to file
            self.save_list_peer(ip, port)

            self.run()

        except Exception as e:
            print(e)
        sys.exit()

    def handler_tcp(self, connection, a):
        print("handle_tcp")
        while True:
            # server recieves the message
            data = connection.recv(self.BUFFER_SIZE)
            for connection in self.connections:
                # The peer that is connected wants to disconnect
                if not data or data.decode('utf-8')[0].lower() == 'q':
                    # disconnect the peer
                    self.disconnect(connection, a)
                    return
                elif data and data.decode('utf-8') == self.REQUEST_STRING:
                    print("-" * 3 + " UPLOADING file NOT IMPLEMENTED " + "-" * 3)
                    # if the connection is still active we send it back the data
                    # this part deals with uploading of the file
                    connection.send(self.msg.encode())
                else:
                    # send back reversed string to client
                    connection.send(data[::-1])
        connection.close()

    def handler_udp(self, client, udp_data):
        # seek for "GET FILE"
        if udp_data and udp_data.decode('utf-8').strip() == self.REQUEST_STRING:
            # send file data
            print("-" * 3 + " UPLOADING file NOT IMPLEMENTED" + "-" * 3)
            self.s.sendto(self.msg.encode(), client)
        else:
            pass


    def run(self):
        # constantly listeen for connections
        connection = []
        data = []
        if self.protocol == 'TCP':
            while True:
                connection, a = self.s.accept()
                # append to the list of peers
                self.peers.append(a)
                print("Peers client are: {}".format(self.peers))
                # self.send_peers()

                # create a thread for a TCP connection
                c_thread = threading.Thread(target=self.handler_tcp, args=(connection, a))
                c_thread.daemon = True
                c_thread.start()
                self.connections.append(connection)
                print("{}, connected TCP".format(a))
                print("-" * 50)

        if self.protocol == 'UDP':
            while True:
                data, client = self.s.recvfrom(1024)
                if data:
                    print('Received data from client %s: %s' % client, data.decode('utf-8'))
                    # create a thread for a UDP connection
                    c_thread = threading.Thread(target=self.handler_udp, args=(client, data))
                    c_thread.daemon = False
                    c_thread.start()
                    print("-" * 50)

    """
        This method is run when the user disconencts
    """
    def disconnect(self, connection, a):
        self.connections.remove(connection)
        self.peers.remove(a)
        connection.close()
        #self.send_peers()
        print("{}, disconnected".format(a))
        print("-" * 50)

    """
        send a list of peers to all the peers that are connected to the server
    """
    def save_list_peer(self, ip, port):
        with open('list_peer_servers.txt', 'a') as outfile:
            outfile.write(str(ip) + ":" + str(port) + "\n")



