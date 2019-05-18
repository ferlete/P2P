import sys
from PyQt5.QtCore import QObject, QThread, pyqtSignal, pyqtSlot
from PyQt5.QtWidgets import QApplication

from P2P.constants import *


def trap_exc_during_debug(*args):
    # when app raises uncaught exception, print info
    print(args)

# install exception hook: without this, uncaught exception would cause application to exit
sys.excepthook = trap_exc_during_debug

class Download(QObject):

    sig_done = pyqtSignal(int)  # worker id: emitted at end of work()
    sig_msg = pyqtSignal(str)  # message to be shown to user
    sig_get_packet = pyqtSignal(int, str, bytes) # packet received

    def __init__(self, id, s, server_address, start, finish, filename):
        """
            class initialization.

            initializes the download class

            Parameters
            ----------
            id : int
                id task
            s: int
               socket
            server_address: str
                ip and port seeder
            start: int
                initial block file
            finish: int
                finish block file
            filename: str
                file name

            Returns
            -------
            nothing

        """
        super().__init__()
        self.__id = id
        self.__abort = False
        self.s = s
        self.server_address = server_address
        self.start = start
        self.finish = finish
        self.filename = filename

    @pyqtSlot()
    def work(self):
        """
        Pretend this worker method does work that takes a long time. During this time, the thread's
        event loop is blocked, except if the application's processEvents() is called: this gives every
        thread (incl. main) a chance to process events, which in this sample means processing signals
        received from GUI (such as abort).
        """
        thread_name = QThread.currentThread().objectName()
        thread_id = int(QThread.currentThreadId())  # cast to int() is necessary
        self.sig_msg.emit('Executando tarefa #{} da thread "{}" start:{} stop:{} (#{})'.format(self.__id, thread_name, self.start, self.finish, thread_id))

        try:

            if int(self.start) == int(self.finish):
                request = SLICE_REQUEST + str(self.start) + ":" + str(self.finish) + ":" + self.filename
                self.s.sendto(request.encode(), self.server_address)
                data, addr = self.s.recvfrom(BUFFER_SIZE)
            else:
                request = SLICE_REQUEST + str(self.start) + ":" + str(self.finish) + ":" + self.filename
                self.s.sendto(request.encode(), self.server_address)
                data, addr = self.s.recvfrom(BUFFER_SIZE)

                while data:
                    self.s.settimeout(2)  # set time out

                    header = (data[:LEN_HEADER].decode())  # header packet
                    id, time_send = header.strip().split(':')
                    packet_id = int(id)

                    self.sig_get_packet.emit(packet_id, time_send, data[LEN_HEADER:])

                    data, addr = self.s.recvfrom(BUFFER_SIZE)

                    # check if we need to abort the loop; need to process events to receive signals;
                    QApplication.processEvents()  # this could cause change to self.__abort
                    if self.__abort:
                        # note that "packet_id" value will not necessarily be same for every thread
                        self.sig_msg.emit('Tarefa #{} abortada no pacote {}'.format(self.__id, packet_id))
                        break

        except Exception as e:
            print(e)

        self.sig_done.emit(self.__id)
        self.s.close()


    @pyqtSlot()
    def abort(self):
        """
            Abord download.

            aborts download tasks

            Returns
            -------
            nothing

        """
        self.sig_msg.emit('Tarefa #{} foi notificada a abortar'.format(self.__id))
        self.__abort = True
        self.notify_server()

    def notify_server(self):
        """
            Notify Seeder.

            notifies seeder to stop sending data

            Returns
            -------
            nothing

        """
        self.s.sendto(KILL_REQUEST.encode(), self.server_address)