import socket
import time
import datetime
import sys
from threading import Thread


class FTP:

	TAG = "FTP"
	sock = None
	running = False
	clientThreads = []

	def __init__(self):
		self.sock = None

	#starts the FTP server
	def start(self):
		if self.sock is None:
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			self.sock.bind(("127.0.0.1", 1921))
			self.sock.listen(3)
			self.running = True
			self.debug("Started")
			while self.sock is not None:
				time.sleep(0.1)
				(clientSocket, address) = self.sock.accept()
				clientThread = Thread(target=self.runClient, args=(clientSocket,))
				clientThread.start()
				self.clientThreads.append(clientThread)

	#Stops the server
	def stop(self):
		self.running = False
		for clientThread in self.clientThreads:
			clientThread.join()
		self.sock.close()
		self.debug("Stopped")

	#Method called per connected client
	def runClient(self, clientSocket):
		self.debug("New client connected")
		
		#Pure-FTPd banner
		clientSocket.send(b'220---------- Welcome to Pure-FTPd [privsep] [TLS] ----------\r\n')
		clientSocket.send(b'220-You are user number 1 of 2 allowed.\r\n')
		now = bytes(datetime.datetime.now().strftime('%H:%M'),'utf-8')
		clientSocket.send(b'220-Local time is now '+ now + b'. Server port: ' + bytes(str(self.port), 'utf-8') + b'.\r\n')
		clientSocket.send(b'220-This is a private system - No anonymous login\r\n')
		clientSocket.send(b'220 You will be disconnected after 15 minutes of inactivity.\r\n')
		
		#Allows basic FTP commands
		cmd_count = 0
		while self.running is True and cmd_count < 10:
			time.sleep(0.1)
			cmd = clientSocket.recv(1024)
			cmd_str = str(cmd, "utf-8") #dangerous in case a byte can't be a character
			cmd_count += 1
			
			if cmd == b'\r\n':
				None
			elif cmd_str.lower().startswith("user ") and len(cmd_str) > 5:
				clientSocket.send(b"331 User "+ bytes(cmd_str[5:], "utf-8") + b" OK. Password required\r\n")
			elif cmd_str.lower().startswith("pass ") and len(cmd_str) > 5:
				time.sleep(5)
				clientSocket.send(b"530 Login authentication failed\r\n")
			else:
				clientSocket.send(b'530 You aren\'t logged in\r\n')

	#Debug output
	def debug(self, msg):
		print((self.TAG + ": " + msg))

				
ftp = FTP()
ftpThread = Thread(target=ftp.start)
ftpThread.start()

time.sleep(20)
ftp.stop()
ftpThread.join(2)
