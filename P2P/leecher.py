import sys
import io
import socket
import threading
import time
import random
import numpy as np
import matplotlib.pyplot as plt
import queue as Q

from PyQt5.QtWidgets import *
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot

from P2P.leecher_UI import Ui_MainWindow
from P2P.peer import Peer
from P2P.constants import *
from P2P.config import Config
from P2P.fileIO import FileIO
from P2P.download import Download

from pydub import AudioSegment
from pydub.playback import play


class Leecher(QWidget):
    count_seeder = 0
    file_size = 0
    num_of_packet = 0
    work_id = 0
    initial_time_download = 0
    last_time_download = 0
    packet_not_player = 0
    packet_real_lost = 0
    number_pause = 0

    packet = []
    packet_lost = []
    packet_delay = []
    packet_send_time = []
    packet_received_time = []
    packet_reproduced_time = []
    buffer_data = []
    buffer_player = []

    seeder_alive = []
    seeder_selected = []
    result_find = []

    file_io = FileIO()
    queue_packet = Q.PriorityQueue()
    _done_buffer = False
    _done_download = False

    RTT = 0.0
    F = 0.0
    Ex = 0.0

    # sig_start = pyqtSignal()  # needed only due to PyCharm debugger bug (!)
    sig_abort_workers = pyqtSignal()

    def __init__(self, parent=None):
        """
            class initialization.

            initializes the Leecher class

            Parameters
            ----------
            nothing

            Returns
            -------
            nothing

        """
        super(Leecher, self).__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setup_signals()
        self.center()
        self.show()
        self.find_seeders_alive()

        self.setup_initial_screen()

        QThread.currentThread().setObjectName('main')  # threads can be named, useful for log output
        self.__workers_done = None
        self.__threads = []

        self.filename_download = ''
        self.filename = ''

    def center(self):
        """
            Center form.

            center the form on the screen

            Returns
            -------
            nothing

        """
        try:

            frameGm = self.frameGeometry()
            centerPoint = QDesktopWidget().availableGeometry().center()
            frameGm.moveCenter(centerPoint)
            self.move(frameGm.topLeft())

        except Exception as ex:
            print(ex)

    def setup_initial_screen(self):
        """
            setup signals.

            initial screen setup

            Returns
            -------
            nothing

        """

        # defines the number of columns and the name of the columns
        header_labels_result = ["ip", "port", "método", "nome arquivo", "tamanho (bytes)"]
        self.ui.tbl_result.setColumnCount(5)
        self.ui.tbl_result.setHorizontalHeaderLabels(header_labels_result)

        # default directory music download
        self.ui.txt_destino.setText(CURRENT_DIR + "/music")

        # set buttons
        self.ui.btn_stop_download.setDisabled(True)
        self.ui.btn_play.setDisabled(True)
        self.ui.btn_graphic.setDisabled(True)

    def setup_signals(self):
        """
            setup signals.

            sets the push button event

            Returns
            -------
            nothing

        """
        try:

            self.ui.btn_find.clicked.connect(self.find_music)
            self.ui.btn_download.clicked.connect(self.start_download)
            self.ui.btn_stop_download.clicked.connect(self.stop_download)
            self.ui.btn_graphic.clicked.connect(self.plot_grafic)
            self.ui.btn_play.clicked.connect(self.play_file)

        except Exception as ex:
            print(ex)

    def find_seeders_alive(self):
        """
            Find seeders alive.

            this function find seeder alive, looking at file list_seeder.txt and showing the amount of active
            seeder in the application footer

            Returns
            -------
            nothing

        """
        try:
            count_peer = 0

            # get seeder alive
            peer = Peer()
            for seeder in peer.get_list_seeder():
                ip, port = seeder.strip().split(':')
                # check for seeder alive
                if peer.check_seeder_alive(str(ip), int(port)):
                    self.seeder_alive.append(seeder)
                    count_peer += 1

            self.count_seeder = count_peer

            if count_peer == 0:
                self.ui.lbl_status.setText(
                    "[-] Rede P2P UDP não possui seeder ativo. Verifique o arquivo %s" % FILENAME_SEEDER)
            else:
                self.ui.lbl_status.setText("[+] Rede P2P UDP tem %d seeder(s) ativo" % count_peer)
        except Exception as ex:
            print(ex)

    @pyqtSlot()
    def stop_download(self):
        """
            Stop download.

            this function sends a signal for all the tasks in parallel to interrupt execution

            Returns
            -------
            nothing

        """
        try:
            self.ui.txt_log.append('Solicitando a cada tarefa o cancelamento')
            self.sig_abort_workers.emit()
            for thread, worker in self.__threads:  # note nice unpacking by Python, avoids indexing
                thread.quit()  # this will quit **as soon as thread event loop unblocks**
                thread.wait()  # <- so you need to wait for it to *actually* quit

            # even though threads have exited, there may still be messages on the main thread's
            # queue (messages that threads emitted before the abort):
            self.ui.txt_log.append('Todas tarefas finalizaram')
        except Exception as ex:
            print(ex)

    def start_download(self):
        """
            start download.

            this function starts downloading the music file according to the selected results

            Returns
            -------
            nothing

        """

        try:
            # checks the selected rows from the table
            indexes = self.ui.tbl_result.selectionModel().selectedRows()
            if len(indexes) == 0:
                QMessageBox.about(self, "Erro", "Selecione um ou mais resultados para fazer download")
            else:

                # load config file
                config = Config()
                self.RTT, self.F, self.Ex = config.load_config()

                self.RTT = float(self.RTT)
                self.F = float(self.F)
                self.Ex = float(self.Ex)

                self.packet_lost = []
                self.packet_delay = []
                self.seeder_selected = []

                # for each selected line, takes the information for ip, port, file name and file size
                for index in sorted(indexes):
                    ip = self.ui.tbl_result.item(index.row(), 0)
                    port = self.ui.tbl_result.item(index.row(), 1)
                    filename = self.ui.tbl_result.item(index.row(), 3)
                    size = self.ui.tbl_result.item(index.row(), 4)

                    self.filename = filename.text()
                    self.file_size = int(size.text())
                    self.seeder_selected.append(ip.text() + ":" + port.text())

                # TODO here we are assuming that in all seeder has the same file size,
                #  however if there is some seerder with same file of different sizes will occur an error

                self.num_of_packet = self.calc_number_chunk(self.file_size)

                # update stats tab
                self.ui.txt_statistic.clear()
                self.ui.txt_statistic.append("Parametros para simulação de perdas: (config.ini)\n")
                self.ui.txt_statistic.append("RTT: " + str(self.RTT))
                self.ui.txt_statistic.append("F: " + str(self.F))
                self.ui.txt_statistic.append("Ex: " + str(self.Ex))
                self.ui.txt_statistic.append("\nTamanho do arquivo (bytes): " + str(self.file_size))
                self.ui.txt_statistic.append("Tamanho do bloco (bytes): " + str(BLOCK_SIZE))
                self.ui.txt_statistic.append("Total de pacotes: " + str(self.num_of_packet))

                # we defined the size of the data receiving array
                self.packet = [False] * self.num_of_packet
                self.packet_send_time = [None] * self.num_of_packet
                self.packet_received_time = [None] * self.num_of_packet
                self.packet_reproduced_time = [None] * self.num_of_packet
                self.buffer_data = [None] * self.num_of_packet

                start = finish = 0
                # here we calculate the number of bytes each seeder should send
                packet_by_seeder = int(self.num_of_packet / len(self.seeder_selected))
                self.initial_time_download = int(round(time.time() * 1000))  # initial time download

                # create to work on a different for player audio
                t = threading.Timer(1, self.player_simulation)
                t.start()

                if self.ui.chk_preview.isChecked():
                    # create to work on a different for preview audio
                    p = threading.Timer(7, self.play_preview)
                    p.start()

                self.ui.btn_download.setDisabled(True)
                self.ui.btn_stop_download.setDisabled(False)
                self.ui.btn_graphic.setDisabled(True)
                self.ui.btn_play.setDisabled(True)

                self.packet_not_player = 0
                self.__workers_done = 0
                self.work_id = 0
                self._done_download = False
                self.number_pause = 0

                for host in self.seeder_selected:
                    ip, port = host.strip().split(':')
                    server_address = (str(ip), int(port))

                    # Create a UDP sockett
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

                    # allow python to use recently closed socket
                    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                    finish = start + packet_by_seeder
                    if finish + 1 == self.num_of_packet:
                        finish += 1

                    # Connect the socket to the port where the server is listening
                    s.connect(server_address)

                    # here we start the parallel work, ie each seeder will receive a request to send part of
                    # your audio file
                    worker = Download(self.work_id, s, server_address, start, finish, self.filename)
                    thread = QThread()
                    self.__threads.append((thread, worker))  # need to store worker too otherwise will be gc'd
                    worker.moveToThread(thread)

                    # get progress and data messages from worker:
                    worker.sig_msg.connect(self.on_worker_msg)
                    worker.sig_get_packet.connect(self.on_get_packet)
                    worker.sig_done.connect(self.on_worker_done)

                    # control worker:
                    self.sig_abort_workers.connect(worker.abort)

                    # get read to start worker:
                    # self.sig_start.connect(worker.work)  # needed due to PyCharm debugger bug (!); comment out
                    # next line
                    thread.started.connect(worker.work)
                    thread.start()  # this will emit 'started' and start thread's event loop

                    self.work_id += 1
                    start = finish

        except Exception as ex:
            print(ex)

    @pyqtSlot(str)
    def on_worker_msg(self, msg):
        self.ui.txt_log.append(str(msg))

    @pyqtSlot(int, str, bytes)
    def on_get_packet(self, packet_id, time_send, data):
        """
            on get packet.

            this function is executed when a package is recedido by the download thread

            Returns
            -------
            nothing

        """

        try:
            milliseconds = int(round(time.time() * 1000))

            # timestamp in ms arrival
            self.packet_send_time[packet_id] = time_send

            # this time and updated in the simulation and loss layer
            self.packet_received_time[packet_id] = milliseconds

            if packet_id != 0:
                arrive = self.simulation_layer_loss_and_delay(packet_id)  # simulation delay and loss
            else:
                arrive = True  # prevents the loss of the initial package

            self.packet[packet_id] = arrive
            if not arrive:
                self.packet_lost.append(packet_id)
                self.ui.txt_log.append('Recebi o pacote #{} * perdido por simulacao'.format(packet_id))
            else:
                self.buffer_data[packet_id] = data
                self.ui.txt_log.append('Recebi o pacote #{}'.format(packet_id))
                self.queue_packet.put((int(packet_id), data))

        except Exception as ex:
            print(ex)

    @pyqtSlot(int)
    def on_worker_done(self, worker_id):
        """
            on work done.

            this function is performed when all parallel download tasks are completed

            Returns
            -------
            nothing

        """
        try:
            self.ui.txt_log.append('tarefa #{} terminou'.format(worker_id))
            self.__workers_done += 1
            if self.__workers_done == self.work_id:
                self.last_time_download = int(round(time.time() * 1000))  # last time download

                self._done_download = True

                self.ui.txt_log.append('Não existe mais tarefas ativas')
                self.ui.btn_download.setDisabled(False)
                self.ui.btn_stop_download.setDisabled(True)
                self.ui.btn_graphic.setDisabled(False)
                self.ui.btn_play.setDisabled(False)

                QMessageBox.about(self, "Informação", "[+] Download finalizado!")

                # save packets to disk
                self.filename_download = self.file_io.save_audio_file(self.filename, self.buffer_data)

                self.ui.btn_play.setDisabled(False)
                self.ui.btn_graphic.setDisabled(False)

                self.update_statistic()

                # save log time send packets to disk
                self.packet_real_lost = self.file_io.save_log_time(self.packet_send_time, self.packet_received_time,
                                                                   self.packet_reproduced_time)
        except Exception as ex:
            print(ex)

    def update_statistic(self):
        """
            Update statistics.

           this function updates the statistics tab with download information

            Returns
            -------
            nothing

        """
        try:
            lost_per = (len(self.packet_lost) / self.num_of_packet) * 100
            lost_delay = ((len(self.packet_lost) + self.packet_not_player) / self.num_of_packet) * 100
            total_secs = ((self.last_time_download - self.initial_time_download) / 1000)
            throughput = (self.file_size * 8) / total_secs
            KB_s = (throughput / 8) / 1000  # Byte-based Transfer Rate Units (current, 1000-based)

            self.ui.txt_statistic.append("Total de pacotes perdidos real: " + str(self.packet_real_lost))
            self.ui.txt_statistic.append("Total de pacotes perdidos por simulação: " + str(len(self.packet_lost)))
            self.ui.txt_statistic.append("Total de pacotes atrasados no player: " + str(self.packet_not_player))
            self.ui.txt_statistic.append(
                "Fração de pacotes não tocados (perdidos por simulação): " + str(lost_per))
            self.ui.txt_statistic.append(
                "Número de Pausas (buffer vazio): " + str(self.number_pause - 2))

            self.ui.txt_statistic.append(
                "Indice de Continuidade: " + str(100 - lost_delay))

            self.ui.txt_statistic.append("Tempo download(segundos): " + str(total_secs))
            self.ui.txt_statistic.append("Throughput (KB/s): " + str(KB_s))
            self.ui.txt_statistic.append("Pacotes perdidos: " + str(self.packet_lost))
            self.ui.txt_statistic.append("Pacotes atrasados: " + str(self.packet_delay))
        except Exception as ex:
            print(ex)

    def find_music(self):
        """
            Find Music.

           this function searches music in the leeders, and prefixes table with the results of the search,
           or shows message of warning if the music is not found in the seeders

            Returns
            -------
            nothing

        """
        try:

            query = self.ui.txt_find.text()

            if query == '':
                QMessageBox.about(self, "Erro", "Informe o nome do arquivo MP3, Exemplo: 3s.mp3")

            else:

                peer = Peer()
                count_result = 0

                # set row count
                self.ui.tbl_result.setRowCount(0)

                for seeder in self.seeder_alive:
                    ip, port = seeder.strip().split(":")

                    size = self.query_file(query, str(ip), int(port))
                    if size > 0:
                        # Create a empty row at bottom of table
                        numRows = self.ui.tbl_result.rowCount()
                        self.ui.tbl_result.insertRow(numRows)

                        policy = peer.get_policy_seeder(str(ip), int(port))
                        item_ip = QTableWidgetItem(ip)
                        item_port = QTableWidgetItem(port)
                        item_policy = QTableWidgetItem(policy)
                        item_filename = QTableWidgetItem(str(query))
                        item_size = QTableWidgetItem(str(size))
                        self.ui.tbl_result.setItem(count_result, 0, item_ip)
                        self.ui.tbl_result.setItem(count_result, 1, item_port)
                        self.ui.tbl_result.setItem(count_result, 2, item_policy)
                        self.ui.tbl_result.setItem(count_result, 3, item_filename)
                        self.ui.tbl_result.setItem(count_result, 4, item_size)
                        count_result += 1

                if count_result == 0:
                    QMessageBox.about(self, "Informação", "Arquivo de audio não encontrado na rede P2P")

        except Exception as ex:
            print(ex)

    def query_file(self, filename, ip, port):
        """
            query file.

            this function queries if there is a certain filename in the seeder

            Parameters
            ----------
            filename : str
                file name
            ip:
                seeder ip
            port:
                seeder port

            Returns
            -------
            int
                Number of bytes in the file. If file does not exist returns 0

        """
        try:
            server_address = (ip, port)

            # Create a UDP socket for first Seeder
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # allow python to use recently closed socket
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Connect the socket to the port where the server is listening
            s.connect(server_address)

            # Send query request to seeder
            request = GET_FILE_REQUEST + filename
            s.sendto(request.encode(), server_address)
            data, server = s.recvfrom(BUFFER_SIZE)
            s.close()

            if data[:7].decode() == EXISTS_RESPONSE:
                file_size = int(data[7:].decode())
            else:
                file_size = 0

            return file_size

        except Exception as ex:
            print(ex)

    def calc_number_chunk(self, bytes):
        """
            Calculate the number of chunks to be created.

            this function calculates the number of blocks that a file has

            Parameters
            ----------
            bytes : int
                amount bytes

            Returns
            -------
            int
                number of chuncks

        """
        try:
            noOfChunks = int(bytes) / BLOCK_SIZE
            if (bytes % BLOCK_SIZE):
                noOfChunks += 1
            return int(noOfChunks)
        except Exception as ex:
            print(ex)

    def simulation_layer_loss_and_delay(self, packet_id):
        """
            loss and delay simulation layer.

            this function performs the loss and delay simulation of packets received by the leecher

            Parameters
            ----------
            packet_id : int
                packet number

            Returns
            -------
            bool
                false if packet is lost or true if packet its ok

        """
        try:

            e = 2.71828

            x = random.uniform(0.0, 100.0)

            if x < self.F:
                return False  # packet lost
            else:
                flag = random.uniform(0.0, 100.0)
                delay = e ** ((-1 / self.Ex) * flag)
                # update new time to packet received
                new_time = int(round(float(self.packet_received_time[packet_id]) + float(self.RTT / 2) + float(delay)))
                self.packet_received_time[packet_id] = new_time

                return True  # packet send with delay

        except Exception as ex:
            print(ex)

    def read_buffer(self, npackets):
        """
            read buffer audio.

            preview audio during downloading

            Returns
            -------
            nothing

        """
        buffer = ''
        num_packet_buffer = len(self.buffer_player)

        if npackets == 0 and num_packet_buffer == 0:
            return buffer
        if num_packet_buffer > npackets:
            buffer = b''.join(self.buffer_player[0:npackets])
            self.buffer_player = self.buffer_player[npackets:]

        else:
            buffer = b''.join(self.buffer_player[0:num_packet_buffer])
            self.buffer_player = self.buffer_player[num_packet_buffer:]

        return buffer

    def player_simulation(self):
        """
            player simulator.

            this function simulates an audio player

            Returns
            -------
            nothing

        """
        try:
            self.buffer_player = []
            last_packet_id = 0
            while not self._done_download:
                while not self.queue_packet.empty():
                    time.sleep(0.013)  # 100 packets of 320 bytes = 1.3322448979591837 seconds
                    packet_id, data = self.queue_packet.get(True, timeout=0.02)

                    milliseconds = int(round(time.time() * 1000))  # timestamp in ms player

                    if packet_id < last_packet_id:  # package arrived late in the player. or discards or requests again.
                        self.packet_not_player += 1
                        self.packet_delay.append(packet_id)
                        self.packet_reproduced_time[packet_id] = milliseconds

                        # TODO improve the implementation of retransmission, for correct reproduction of the audio
                        #self.retransmit_packet(next[0])
                        #time.sleep(DELAY_FOR_SEND * 4)

                    else:
                        last_packet_id = packet_id
                        self.buffer_player.append(data)
                        self.packet_reproduced_time[last_packet_id] = milliseconds

                time.sleep(1)  # wait 1 second to accumulate packets in the buffer
                self.number_pause += 1  # Buffer empty

            self._done_buffer = True

        except Exception as ex:
            print(ex)

    # TODO this function must be improved to support a thread pool
    def retransmit_packet(self, packet_id):

        try:

            ip, port = self.seeder_selected[0].strip().split(':')
            server_address = (str(ip), int(port))

            # Create a UDP sockett
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            # allow python to use recently closed socket
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

            # Connect the socket to the port where the server is listening
            s.connect(server_address)

            reworker = Download(self.work_id, s, server_address, packet_id, packet_id, self.filename)
            thread = QThread()
            self.__threads.append((thread, reworker))  # need to store worker too otherwise will be gc'd
            reworker.moveToThread(thread)

            # get progress and data messages from worker:
            reworker.sig_msg.connect(self.on_worker_msg)
            reworker.sig_get_packet.connect(self.on_get_packet)
            reworker.sig_done.connect(self.on_worker_done)

            # control worker:
            self.sig_abort_workers.connect(reworker.abort)

            # get read to start worker:
            # self.sig_start.connect(worker.work)  # needed due to PyCharm debugger bug (!); comment out
            # next line
            thread.started.connect(reworker.work)
            thread.start()  # this will emit 'started' and start thread's event loop

            self.work_id += 1
        except Exception as ex:
            print(ex)

    def play_preview(self):
        """
           preview audio while downloading.

            preview audio during downloading

            Returns
            -------
            nothing

        """
        try:
            data = self.read_buffer(500)
            seg = AudioSegment.from_file(io.BytesIO(data), format="mp3")
            print("[+] Preview Duration:", seg.duration_seconds, "seconds")
            play(seg)

        except Exception as ex:
            print(ex)

    # TODO to make an asynchronous audio player with data buffer
    def play_music_on_download(self):
        try:
            data = self.read_buffer(30)
            while data != b'':
                seg = AudioSegment.from_file(asyncio.BytesIO(data), format="mp3")
                # seg = seg.set_frame_rate(16000)
                # samples = seg.get_array_of_samples()
                # print("[+] Samples:", samples)
                print("[+] Duration:", seg.duration_seconds, "seconds")
                print("[+] Sampling frequency:", seg.frame_rate)
                print("[+] Bits per sample:", seg.sample_width * 8)
                # print(seg.raw_data)
                play(seg)
                # time.sleep(seg.duration_seconds)
                data = self.read_buffer(30)


        except Exception as ex:
            print(ex)
            sys.exit()

    def play_file(self):
        """
            play file audio.

            play music

            Returns
            -------
            nothing

        """
        try:

            # create to work on a different for play file
            p = threading.Thread(target=self.play_music, args=[self.filename_download])
            p.start()

        except Exception as ex:
            print(ex)

    def play_music(self, filename):
        """
            play audio.

            play music after downloading

            Returns
            -------
            nothing

        """
        try:
            seg = AudioSegment.from_file(filename, format="mp3")
            print("[+] Audio Information")
            print("[+] Channels:", seg.channels)
            print("[+] Bits per sample:", seg.sample_width * 8)
            print("[+] Sampling frequency:", seg.frame_rate)
            print("[+] Length:", seg.duration_seconds, "seconds")
            play(seg)  # play audio
        except Exception as ex:
            print(ex)

    def plot_grafic(self):
        """
            plot graphic.

            plot graphic with time send, receive and play

            Returns
            -------
            nothing
        """
        try:
            x, y, z, w = np.loadtxt(FILENAME_TIME, comments='#', delimiter=':', unpack=True)

            plt.plot(y, x, label='Transmitido', linewidth=1.0)
            # when the packet is lost it is marked as x in the graph
            plt.plot(z, x, '-rx', label='Recebido', linewidth=0.5, markevery=self.packet_lost)
            plt.plot(w, x, '-r+', label='reproduzido', linewidth=0.5, markevery=self.packet_delay)
            plt.xlabel('Tempo (timestamp)')
            plt.ylabel('Número do Pacote')
            plt.title('Tradeoff')
            plt.grid(True)
            plt.legend(loc=2, ncol=2)
            plt.show()

        except Exception as ex:
            print(ex)
