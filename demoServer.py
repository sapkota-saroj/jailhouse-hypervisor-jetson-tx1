# UDP Face Watch Video Server

from threading import Thread
import socket
import sys
import cv2
import time
import numpy

UDP_IP = "131.230.193.220"
	# This is the Server's IP Address, you should change it to your IP Address

UDP_PORT = 5052
	# This is the Server's Port. It doesn't really matter which port you choose, as long as you choose one not in use

BUFFER_SIZE = 1024
	# This is the Buffer size. It should match the buffer size of client side application

DEBUG = True
	# This will print some extra information if set to True

CV_WINDOW_NAME = "Server"

TIMEOUT = 30

G_STOP = False

MONITOR = -1 # will show what the server sees from this connection. Useful for debugging. Set to -1 to disable

class connection:
	def __init__(self, addr, args, threadCount):
		if(DEBUG):
			print("Initalizing Connection")
		self.last_update = time.time()
		self.client_addr = addr
		self.name = threadCount
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.bind((UDP_IP, 0))
		self.latency = None
		self.CTTC = None
		self.C_maxRes = None
		self.C_minRes = None
		self.C_res = None
		self.STTC = None
		self.stopped = True
		self.cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
		

	def start(self):
		print("I'm on start")
		self.sock.settimeout(TIMEOUT)
		packet = None
		TER_code = -1 # Message was either not from client or was not DAT*
		try:
			packet, addr = self.sock.recvfrom(BUFFER_SIZE)
			print("packet=",packet)
			print("addr=",addr)
		except:
			if(DEBUG):
				print("Connection " + str(self.name) + " timed out")
			self.terminate(-2) # Client Timed Out
			return
		rcvTime = time.time()
		if(len(packet) < 4):
			self.terminate(-3) # Client didn't send a valid packet
			return

		tag = packet[:4].decode('utf-8', 'ignore')
		print("tag=",tag)
		if(addr == self.client_addr and tag == "DAT*"):
			content = packet[4:].decode('utf-8', 'ignore')
			data = content.split('<')
			if(len(data) > 1):
				self.latency = float(data[0]) - rcvTime
				self.localTTC = float(data[1])
				self.stopped = False
				print("goining to listen")
				TER_code = self.listen()
		self.terminate(TER_code)
		return
	
	def terminate(self, TER_code):
		print(TER_code)
		self.sock.sendto(("TER*"+str(TER_code)).encode('utf-8'), self.client_addr)
		self.stopped = True
		self.sock.close()
		if(DEBUG):
			print("Terminating Connection " + str(self.name))
		if(self.name is MONITOR):
			cv2.destroyWindow(str(self.name))


	def listen(self):
		print("i'm on listen")
		if(self.stopped):
			return
		print("Listenting to Connection " + str(self.name))
		length = 99999999
		data = []
		self.sock.settimeout(TIMEOUT)
		while(not self.stopped and not G_STOP):
			while(length > len(data)):
				packet = None
				try:
					packet, addr = self.sock.recvfrom(BUFFER_SIZE)
					#print("packet=",packet)
					#print("addr=",addr)
				except:
					return -2 # Client Timed Out
				
				if(addr[0] != self.client_addr[0]):
					continue

				if(len(packet) < 4):
					data.clear()
					continue

				self.last_update = time.time()
				tag = packet[:4].decode('utf-8', 'ignore')
				#print("tag=",tag)
				if(tag == "LEN*"):
					temp_length = packet[4:].decode('utf-8','ignore')
					length=int(float(temp_length))
					#length = int(packet[4:].decode('utf-8','ignore'))
					#print("length=",length)
					data.clear()

				elif(tag == "KAL*"):
					print('KAL*')
					self.last_update = time.time()

				elif(tag == "DAT*"):
					data = packet[4:].decode('utf-8', 'ignore')
					if(len(data) > 1):
						self.latency = float(data[0]) - rcvTime
						self.localTTC = float(data[1])

				elif(tag == "TER*"):
					return 0 # Connection Terminated by client

				else:
					data.append(packet)

			code = 0
			try:
				bstream = b"".join(data)
				data.clear()
				code+=1
				encoded_img = numpy.fromstring(bstream, numpy.uint8)
				if(encoded_img is None):
					#if(DEBUG):
					print("Image " +str(self.name) + "was corrupted.code: " +str(code))
				code+=1
				image = cv2.imdecode(encoded_img, cv2.IMREAD_GRAYSCALE)
				#print (image)
			except:
				self.sock.sendto("ERR*".encode('utf-8'), self.client_addr)
				if(DEBUG):
					print("Image " + str(self.name) + " was corrupted. Code: " + str(code))
				continue
			data.clear()
			if(image is None):
				if(DEBUG):
					print("Image " + str(self.name) + " was corrupted. Code: 3")
				continue
			if(self.name is MONITOR):
				cv2.imshow(str(self.name), image)
				cv2.waitKey(1)
			faces = self.cascade.detectMultiScale(image, 1.3, 5)
			
			response = "FAC*"
			for(x,y,w,h) in faces:
				response += ("<" + str(x) + "|" + str(y) + "|" + str(w))
			self.sock.sendto(response.encode('utf-8'), self.client_addr)
		return -4 # Connection was stopped by the Server

	def stop(self):
		self.stopped = True

	def get_original_addr(self):
		return self.original_addr

	def get_last_update(self):
		return self.last_update

	def get_server_IP(self):
		return self.sock.getsockname()[0]
	def get_server_port(self):
		return self.sock.getsockname()[1]

class hook:
	def __init__(self, sock):
		self.sock = sock
		self.stopped = True

	def start(self):
		self.stopped = False
		print("go to start")
		Thread(target=self.update, args = ()).start()
		
	def stop(self):
		self.stopped = True

	def update(self):
		if(self.stopped):
			return
		threadCount = 1
		self.sock.settimeout(5)
		while(not self.stopped and not G_STOP):
			try:
				packet, addr = self.sock.recvfrom(BUFFER_SIZE)
			except:
				continue
			if(len(packet) < 4):
				continue
			tag = packet[:4].decode('utf-8', 'ignore')
			if(tag == "HSK*"):
				args = packet[4:].decode('utf-8', 'ignore')
				x = connection(addr,args,threadCount)
				self.sock.sendto(("HSK*<"+x.get_server_IP()+"<"+str(x.get_server_port())).encode("utf-8"), addr)
				Thread(target=x.start, args = ()).start()
				threadCount += 1
		return


def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.bind((UDP_IP, UDP_PORT))
	x = hook(sock)
	if(DEBUG):
		print("Start")
	x.start()
	input("Press Enter to Quit")
	print("Closing Threads...")
	global G_STOP
	G_STOP = True
	x.stop()
	sock.close()
	
	

if __name__ == "__main__":
	main()
