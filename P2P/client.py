import socket
import sys
import threading


class Client:

    BUFFER_SIZE = 1024
    REQUEST_STRING = "GET FILE"
    previous_data = None

    def __init__(self, ip, port):
        try:
            # Create a TCP/IP socket
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            # allow python to use recently closed socket
            self.s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Connect the socket to the port where the server is listening
            server_address = (ip, port)
            print('connecting to %s:%s' % server_address)
            self.s.connect(server_address)

            # create to work on a different thread
            i_thread = threading.Thread(target=self.send_message)
            i_thread.daemon = True
            i_thread.start()

            while True:

                r_thread = threading.Thread(target=self.recieve_message)
                r_thread.start()
                r_thread.join()

                data = self.recieve_message()

                if not data:
                    # means the server has failed
                    print("-" * 21 + " Server failed " + "-" * 21)
                    break

                elif data[0:1] == b'\x11':
                    print("Got peers")
                    # first byte is the byte '\x11 we added to make sure that we have peers


            #self.sendmessage("GET FILE")

            #self.s.close()

        except Exception as e:
            print(e)
        sys.exit()

    def send_message(self):
        try:
            # encode the message into bytes
            # other code will run when this happens as the thread is busy
            # request to download the file
            self.s.send(self.REQUEST_STRING.encode('utf-8'))

            # check if the user wants to quit the connection
            # if data[0:1].lower() == "q":
            #    self.send_disconnect_signal()

        except KeyboardInterrupt as e:
            # If a user turns the server off due to KeyboardInterrupt
            self.send_disconnect_signal()
            return

    def recieve_message(self):
        try:
            print("Recieving -------")
            data = self.s.recv(self.BUFFER_SIZE)

            print(data.decode("utf-8"))

            print("\nRecieved message on the client side is:")

            if self.previous_data != data:
                #fileIO.create_file(data)
                self.previous_data = data
            # TODO download the file to the computer

            return data
        except KeyboardInterrupt:
            self.send_disconnect_signal()

    def send_disconnect_signal(self):
        print("Disconnected from server")
        # signal the server that the connection has closed
        self.s.send("q".encode('utf-8'))
        sys.exit()
