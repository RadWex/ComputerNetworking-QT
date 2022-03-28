import socket
import sys
from threading import Thread, Lock
from PyQt5.QtWidgets import *


class MySocket(Thread):
    def __init__(self, output, sock=None):
        Thread.__init__(self)
        self.interface = output
        self.thread_active = True
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        try:
            self.sock.bind((host, port))
        except:
            return 1, "Address already in use: NET_Bind"
        return 0, "Server is working on port " + str(port)

    def run(self):
        while self.thread_active:
            data, addr = self.sock.recvfrom(1024)
            self.interface.append(
                str(addr) + " | size: " + str(len(data)) + " : " + data.decode())
            self.sock.sendto(data, addr)

    def myclose(self):
        self.thread_active = False
        self.sock.close()


class MainWidow(QWidget):
    def __init__(self):
        super().__init__()
        self.output_text = QTextEdit()
        self.socket_ins = MySocket(self.output_text)
        grid = QGridLayout()
        self.setLayout(grid)
        grid.addWidget(QLabel("Listening port"), 0, 0)
        self.port_text = QLineEdit("8000")
        grid.addWidget(self.port_text, 0, 1)
        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.connect)
        grid.addWidget(self.start_button, 0, 3)
        grid.addWidget(self.output_text, 2, 0, 1, 6)
        self.show()

    def connect(self):
        err_code, output = self.socket_ins.connect("localhost",
                                                   int(self.port_text.text()))
        self.output_text.append(output)
        if (err_code == 0):
            self.output_text.append("Waiting for new message")
            self.socket_ins.start()

    def closeEvent(self, event):
        self.socket_ins.myclose()  # close socket on exit


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWidow()
    sys.exit(app.exec_())
