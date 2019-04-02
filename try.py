import base64, copy, thread, signal
import socket, sys, os, time
import datetime, json, email.utils, threading

config = {
    'HOST_NAME': '127.0.0.1',
    'BIND_PORT': 20100,
    'MAX_REQUEST_LEN': 1024
}

class Server:

    def __init__(self):

        self.client_name = 1
        
        try:
            signal.signal(signal.SIGINT, self.shutdown)
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((config['HOST_NAME'], config['BIND_PORT']))
            self.server_socket.listen(100)
            # self.__clients = {}
        except Exception as e:
            '''error functionality in initializing socket'''
            print e
            quit()

        while True:
            # try except here
            (client_socket, client_address) = self.server_socket.accept()
            thread_ = threading.Thread(
                name = self._getClientName(), 
                target = self.proxy_thread,
                args = (client_socket, client_address))
            thread_.setDaemon(True)
            thread_.start()
    
    def proxy_thread(self, client_socket, client_address):
        request = client_socket.recv(config['MAX_REQUEST_LEN'])
        print request
     #    first_line = request.split('\n')[0]
     #    url = first_line.split(' ')[1]
     #    http_pos = url.find("://")
        # if (http_pos==-1):
        #     temp = url
        # else:
        #     temp = url[(http_pos+3):]

        # port_pos = temp.find(":")
        # webserver_pos = temp.find("/")

        # if webserver_pos == -1:
        #     webserver_pos = len(temp)

        # webserver = ""
        # port = -1
        # if (port_pos==-1 or webserver_pos < port_pos): 
        #     port = 80 
        #     webserver = temp[:webserver_pos] 

        # else:
        #     port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
        #     webserver = temp[:port_pos]

        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        # s.settimeout(config['CONNECTION_TIMEOUT'])
        # s.connect((webserver, port))
        # s.sendall(request)

        # while 1:
     #    # receive data from web server
     #    data = s.recv(config['MAX_REQUEST_LEN'])

     #    if (len(data) > 0):
     #        client_socket.send(data) # send to browser/client
     #    else:
     #        break

    def shutdown(self):
        print "shutdown called"
        quit()

    def _getClientName(self):
        self.client_name += 1
        return self.client_name

newserver = Server()