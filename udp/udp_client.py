import socket
import sys
from PyQt5.QtWidgets import *


class MySocket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_DGRAM)
        else:
            self.sock = sock

    def mysend(self, msg, host, port):
        msg = msg.encode()
        self.sock.sendto(msg, (host, port))

    def myreceive(self, rec_leng):
        self.sock.settimeout(0.2)
        try:
            resp, server_address = self.sock.recvfrom(1024)
            resp = resp.decode()
        except:
            resp = "Didn't receive data! [Timeout]"
        return resp

    def myclose(self):
        self.sock.close()


class MainWidow(QWidget):
    def __init__(self):
        super().__init__()
        self.socket_ins = MySocket()
        grid = QGridLayout()
        self.setLayout(grid)
        grid.addWidget(QLabel("TCP server IP or domain name"), 0, 0)
        self.ip_text = QLineEdit("localhost")
        grid.addWidget(self.ip_text, 0, 1)
        grid.addWidget(QLabel("TCP server port"), 0, 2)
        self.port_text = QLineEdit("8000")
        grid.addWidget(self.port_text, 0, 3, 1, 2)

        grid.addWidget(QLabel("Message to sent"), 1, 0)
        self.message_text = QLineEdit("Something to send")
        grid.addWidget(self.message_text, 1, 1, 1, 3)
        self.send_button = QPushButton("Send")
        self.send_button.clicked.connect(self.send)
        grid.addWidget(self.send_button, 1, 4)
        self.output_text = QTextEdit()
        grid.addWidget(self.output_text, 2, 0, 1, 6)
        self.show()

    def send(self):
        text_output = self.message_text.text()
        self.message_text.setText("")
        self.socket_ins.mysend(
            text_output, self.ip_text.text(), int(self.port_text.text()))
        self.output_text.append("TO SERVER: " + text_output)
        text_input = self.socket_ins.myreceive(len(text_output))
        self.output_text.append("FROM SERVER: " + text_input)
        self.socket_ins.myclose()
        self.socket_ins = MySocket()

    def closeEvent(self, event):
        self.socket_ins.myclose()  # close socket on exit


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = MainWidow()
    sys.exit(app.exec_())
