import http.server
import socketserver
import sys
import os
from urllib import parse

PORT = 8080


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_HEAD(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()

    def do_GET(self):
        sum_val = 0
        num = []
        message = "<HTML><BODY><table border='1'>"
        path = self.path
        while True:
            tmp = path.find('_')
            if(tmp == -1):
                num.append(path[len(path)-1])
                break
            num.append(path[tmp-1])
            path = path[tmp+1:]

        for i in num:
            try:
                with open(os.path.dirname(os.path.abspath(__file__)) + '/' + str(i)+'.txt', 'r') as f:
                    line = f.readlines()
            except:
                message = "The storage does not exist or you have typed the wrong url! Enter e.g. http://localhost:8080/1"
                break
            for i in line:
                message += i
                if(i.find('<td>') == -1):
                    continue
                tmp = i[i.find('<td>')+4:i.find('</td>')]
                if(tmp.isdigit()):
                    sum_val += int(tmp)

        message += "</table>"
        message += "<br>Sum: "+str(sum_val)
        message += "</BODY></HTML>"
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(message.encode())


with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
