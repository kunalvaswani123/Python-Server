import base64, copy, thread, signal
import socket, sys, os, time, struct
import datetime, json, email.utils, threading

config = {
    'HOST_NAME': '127.0.0.1',
    'BIND_PORT': 20100,
    'MAX_REQUEST_LEN': 1024,
    'BUFFER_SIZE': 100000000,
    'CONNECTION_TIMEOUT' : 20
}

file = open("blacklist.txt","r")
blocked_files = file.readlines()
blocked_list = []

for ips in blocked_files:
	(ip, cidr) = ips.split('/')
	cidr = int(cidr) 
	host_bits = 32 - cidr
	i = struct.unpack('>I', socket.inet_aton(ip))[0]
	start = (i >> host_bits) << host_bits
	end = start | ((1 << host_bits))
	end += 1
	for i in range(start, end):
	    blocked_list.append(socket.inet_ntoa(struct.pack('>I',i)))

class Server:

    def __init__(self):

    	Cache = "./cache"

    	if not os.path.isdir(Cache):
    		os.makedirs(Cache)

        for files in os.listdir(Cache):
        	temp = Cache + "/" + files
        	os.remove(files)
        
        self.client_name = 1
        
        try:
            signal.signal(signal.SIGINT, self.shutdown)
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind((config['HOST_NAME'], config['BIND_PORT']))
            self.server_socket.listen(100)
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
        first_line = request.split('\n')[0]
        url = first_line.split(' ')[1]
        http_pos = url.find("://")
        temp_index = 0
        if (http_pos==-1):
            temp_index = 0
        else:
            temp_index = http_pos + 3
        temp = url[temp_index:]
        port_pos = temp.find(":")
        webserver_pos = temp.find("/")

        if webserver_pos == -1:
            webserver_pos = len(temp)

        webserver = ""
        port = -1
        if (port_pos == -1 or webserver_pos < port_pos): 
            port = 80 
            webserver = temp[:webserver_pos] 

        else:
            port = int(temp[port_pos + 1 : webserver_pos])
            webserver = temp[:port_pos]

        val = socket.gethostbyname(webserver)
    	if val in blocked_list:
    		client_socket.send("Page Blocked")
    		sys.exit(0)

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.settimeout(config['CONNECTION_TIMEOUT'])
        s.connect((webserver, port))
        # s.sendall(request)

        # while True:

        #     data = s.recv(config['BUFFER_SIZE'])
        #     if (len(data) > 0):
	       #      client_socket.send(data)
        #     else:
       
        #         break
        try:
        	fname = temp.split('/')[1]
        except IndexError:
        	fname = '/'

        if fname in os.listdir(Cache):
        	t1 = ""
        	t1 = t1 + "GET /"
        	t1 = t1 + fname
        	t1 = t1 + " HTTP/1.1\r\nIf-Modified-Since: "
        	t1 = t1 + time.ctime(os.path.getmtime(Cache + fname))
        	t1 = t1 + " \r\n\r\n"
        	s.send(t1)
        else:
        	t1 = ""
        	t1 = t1 + "GET "
        	t1 = t1 + fname
        	t1 = t1 + " HTTP/1.1\r\n\r\n"
        	s.send(t1)

        response = s.recv(config['MAX_REQUEST_LEN'])

        current_time = time.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
        logs[url].append({
        	"mtime" : current_time,
        	"data" : response
        	})
        if(len(logs[url]) > 4):
        	del logs[url][0]

        if response.find("304") >= 0:
        	t2 = Cache + fname
        	file_pointer = open(os.path(t2), 'rb')
        	temp_var = file_pointer.read(config['MAX_REQUEST_LEN'])
        	while(temp_var):
        		client_socket.send(temp_var)
        		temp_var = file_pointer.read(config['MAX_REQUEST_LEN'])
        	file_pointer.close()
        
        elif response.find("200") >= 0:
        	t2 = Cache + fname
        	flag = 0
    		ctime = time.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")	
        	if(ctime - logs[url][-3] < 300):
        		flag = 1
        	file_pointer = open(os.path(t2), 'wb')
        	while true:	
        		if(len(response) == 0):
        			break
        		if(flag == 1):
        			file_pointer.write(response)
        		client_socket.send(response)
        		response = s.recv(config['MAX_REQUEST_LEN'])
        	file_pointer.close()		

        s.close()
        client_socket.close()	

    def shutdown(self):
        print "shutdown called"
        quit()

    def _getClientName(self):
        self.client_name += 1
        return self.client_name

    # def cache_delete():

    # 	min_time = min(os.path.getmtime(Cache + "/" + files) for files in os.listdir(Cache))
    # 	last_file = ""
    # 	for files in os.listdir(Cache):
    # 		if(os.path.getmtime(Cache + "/" + files) == min_time)
    # 			last_file = files[0]

    # 	os.remove(Cache + "/" + last_file)		
    
    # def cache_file_info(fileurl):

    # 	if(fileurl[0] == '/'):
    # 		fileurl = fileurl[1:]

    # 	fileurl = fileurl.replace("/", "__")
    # 	path = Cache + "/" + fileurl

    # 	if(os.path.isfile(path)):
    #     	ltime = time.strptime(time.ctime(os.path.getmtime(path)), "%a %b %d %H:%M:%S %Y")
    #     	return path, ltime
    # 	else:
    # 		return path, None

    # def cache_file_info(fileurl):

    # 	if(fileurl[0] == '/'):
    # 		fileurl = fileurl[1:]

    # 	fileurl = fileurl.replace("/", "__")
    # 	path = Cache + "/" + fileurl

    # 	if(os.path.isfile(path)):
    #     	ltime = time.strptime(time.ctime(os.path.getmtime(path)), "%a %b %d %H:%M:%S %Y")
    #     	return path, ltime
    # 	else:
    # 		return path, None	

    # def add_url(url, client_address):
    	
    # 	url = url.replace("/", "__")
    # 	if url in logs:
    # 		current_time = time.strptime(time.ctime(), "%a %b %d %H:%M:%S %Y")
    # 		logs[url].append({
    # 			"mtime" : current_time,
    # 			"client" : json.dumps(client_address)
    # 			})
    # 		if(len(logs[url]) > 3):
    # 			del logs[url][0]

logs = {}
newserver = Server()
