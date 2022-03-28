import socket
import time
import sys
import struct
from threading import Thread, Lock
from PyQt5.QtWidgets import *
socket.SO_REUSEPORT = socket.SO_REUSEADDR


class MySocket(Thread):
    def __init__(self, output, sock=None):
        Thread.__init__(self)
        self.interface = output
        self.thread_active = True
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                      socket.IPPROTO_UDP)
        else:
            self.sock = sock

    def get_Host_name_IP(self):
        try:
            host_name = socket.gethostname()
            host_ip = socket.gethostbyname(host_name)
            print("Hostname :  ", host_name)
            print("IP : ", host_ip)
            return host_ip
        except:
            print("Unable to get Hostname and IP")
            return "<broadcast>"

    def get_broadcast_IP(self):
        ip = self.get_Host_name_IP()
        return ip[:(ip.rfind(".")+1)]+"255"

    def mysend(self, msg, host, port=8000):
        self.sock.setsockopt(
            socket.IPPROTO_IP, socket.IP_MULTICAST_IF, socket.INADDR_ANY)
        ttl = struct.pack('b', 1)
        msg = msg.encode()
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, ttl)
        try:
            sent = self.sock.sendto(msg, (host, port))
        except:
            return 1, "Valid address"
        return 0, msg.decode()

    def connect(self, host, port=8000):
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # self.sock.settimeout(0.2)
        try:
            self.sock.bind(("", port))
        except:
            return 1, "Address already in use: NET_Bind"
        group = socket.inet_aton(host)
        mreq = struct.pack('4sL', group, socket.INADDR_ANY)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        return 0, "Listening on port " + str(port)

    def run(self):
        while self.thread_active:
            try:
                data, addr = self.sock.recvfrom(1024)
                self.interface.append(
                    str(addr) + " | size: " + str(len(data)) + " : " + data.decode())
                print(data.decode())
            except:
                pass

    def myclose(self):
        self.thread_active = False
        self.sock.close()


class MainWidow(QWidget):
    def __init__(self):
        super().__init__()
        self.output_text = QTextEdit()
        self.socket_send = MySocket(self.output_text)
        self.socket_recv = MySocket(self.output_text)
        grid = QGridLayout()
        self.setLayout(grid)
        self.setWindowTitle("Multicasting")
        grid.addWidget(QLabel("Multicast group IP"), 0, 0)
        self.ip_text = QLineEdit("224.0.0.10")
        grid.addWidget(self.ip_text, 0, 1)
        grid.addWidget(QLabel("Listening port"), 0, 2)
        self.port_text = QLineEdit("8000")
        grid.addWidget(self.port_text, 0, 3)
        self.start_button = QPushButton("Start listening")
        self.start_button.clicked.connect(self.startListenign)
        grid.addWidget(self.start_button, 0, 4)
        self.stop_listening_button = QPushButton("Stop")
        self.stop_listening_button.clicked.connect(self.stopListening)
        self.stop_listening_button.setEnabled(False)
        grid.addWidget(self.stop_listening_button, 0, 5)
        grid.addWidget(QLabel("Message to sent"), 1, 0)
        self.message_text = QLineEdit("Something to send")
        grid.addWidget(self.message_text, 1, 1, 1, 4)
        self.send_button = QPushButton("Send")
        self.stop_listening_button.setEnabled(False)
        self.send_button.clicked.connect(self.send)
        grid.addWidget(self.send_button, 1, 5)
        grid.addWidget(self.output_text, 2, 0, 1, 6)
        self.show()

    def startListenign(self):
        self.socket_recv = MySocket(self.output_text)
        try:
            port = int(self.port_text.text())
        except:
            port = 8000
        err_code, output = self.socket_recv.connect(self.ip_text.text(), port)
        self.output_text.append(output)
        if (err_code == 0):
            self.output_text.append("Waiting for new message")
            self.socket_recv.start()
            self.stop_listening_button.setEnabled(True)
            self.start_button.setEnabled(False)

    def send(self):
        text_output = self.message_text.text()
        self.message_text.setText("")
        try:
            port = int(self.port_text.text())
        except:
            port = 8000
        err_code, txt = self.socket_send.mysend(
            text_output, self.ip_text.text(), port)
        if (err_code == 0):
            self.socket_send.myclose()
            self.socket_send = MySocket(self.output_text)
        else:
            self.output_text.append(txt)

    def stopListening(self):
        self.start_button.setEnabled(True)
        self.stop_listening_button.setEnabled(False)
        self.socket_recv.myclose()
        self.output_text.append("Socket close")

    def closeEvent(self, event):
        self.socket_send.myclose()  # close socket on exit
        self.socket_recv.myclose()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWidow()
    sys.exit(app.exec_())
