import socket
import time
import datetime
import sys
from threading import Thread


class FTP:

	TAG = "FTP"
	
	host = None
	port = None

	sock = None
	running = False

	clients = {}

	def __init__(self, host, port):
		self.sock = None
		self.host = host
		self.port = port

	#starts the FTP server
	def start(self):
		if self.sock is None:
			
			#socket initialization
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
			self.sock.bind((self.host, self.port))
			self.sock.settimeout(3)
			self.sock.listen(3)

			self.running = True
			self.debug("Server Started")

			#main thread loop, waiting for clients to connect
			while True:
				
				if self.running == 0:
					break
				try:
					#waiting for a client to connect
					(clientSocket, address) = self.sock.accept()
					ip = str(address[0]) + ":" + str(address[1])


					#starting the client thread
					clientThread = Thread(target=self.runClient, args=(clientSocket,ip))
					clientThread.start()

					#saving the client's socket
					self.clients[ip] = {'socket': clientSocket, 'thread': clientThread}

				except:
					pass

			self.sock.close()
			self.debug("Server stopped")


	#Stops the server
	def stop(self):
		self.debug("Stopping server and closing active connections")
		self.running = False

		for ip,client in self.clients.items():
			self.debug("["+ ip + "] Disconnecting")
			try:
				client['socket'].shutdown(socket.SHUT_RDWR)
			except:
				pass
			client['thread'].join()

	#Method called per connected client
	def runClient(self, clientSocket, ip):

		self.debug("["+ ip + "] Client Connected")

		#Pure-FTPd banner
		clientSocket.send(b'220---------- Welcome to Pure-FTPd [privsep] [TLS] ----------\r\n')
		clientSocket.send(b'220-You are user number 1 of 2 allowed.\r\n')
		now = bytes(datetime.datetime.now().strftime('%H:%M'),'utf-8')
		clientSocket.send(b'220-Local time is now '+ now + b'. Server port: ' + bytes(str(self.port), 'utf-8') + b'.\r\n')
		clientSocket.send(b'220-This is a private system - No anonymous login\r\n')
		clientSocket.send(b'220 You will be disconnected after 15 minutes of inactivity.\r\n')
		
		#Allows basic FTP commands
		while True:
			time.sleep(0.1)
			
			try: 
				cmd = clientSocket.recv(1024)
				cmd_str = str(cmd, "utf-8") #dangerous in case a byte can't be a character
				
				if cmd == b'\r\n':
					None
				elif cmd_str.lower().startswith("user ") and len(cmd_str) > 5:
					clientSocket.send(b"331 User "+ bytes(cmd_str[5:], "utf-8") + b" OK. Password required\r\n")
				elif cmd_str.lower().startswith("pass ") and len(cmd_str) > 5:
					time.sleep( round((time.time() % 4) + 1) )
					clientSocket.send(b"530 Login authentication failed\r\n")
				else:
					clientSocket.send(b'530 You aren\'t logged in\r\n')
			except:
				break

		clientSocket.close()
		self.debug("["+ ip + "] Client disconnected")

	#Debug output
	def debug(self, msg):
		print((self.TAG + ": " + msg))

	def getStatus(self):
		status = "Client List: "
		for ip,client in self.clients.items():
			status += "["+ ip + "] "

		return status






ftp = FTP("127.0.0.1", 1921)
ftpThread = Thread(target=ftp.start)
ftpThread.start()

quit = False
while quit == False:
	cmd = input('Type q to quit, l to list clients\n')

	if cmd == 'q' or cmd == 'quit':
		quit = True
	if cmd == 'l' or cmd == 'list':
		print(ftp.getStatus())

ftp.stop()
ftpThread.join()
