# Face Detect Pipelined
import socket
import cv2
import time
from math import ceil
from threading import Thread

CV_WINDOW_NAME = "Face Detection"
	# This is the name of the Window that opens, it can be changed to any string

#UDP_IP = "131.230.191.195"
UDP_IP = "131.230.193.220"
	# This is the IP of the server that the program will attempt to connect to
    
UDP_PORT = 5052
	# This is the Port number of the server that the program will try to connect to when setting up the handshake
    
BUFFER_SIZE = 1024
	# This is the buffer size of the UDP packets that are sent by this program, changing it doesn't seem to make much of a difference
	
CHECK_RATE = 0.001
	# Defines how much time elapses between each check for pipe completion. Reducing it can lead to very slight gains in performance, however this will greatly increase processing cost

TIMEOUT = 5 #Determines how long the program will continue without a response


VIDEO = cv2.VideoCapture(0)
VIDEO.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
VIDEO.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
cv2.namedWindow(CV_WINDOW_NAME)


def terminate(sock):
	try:
		sock.send('TER*'.encode('utf-8'))
	except:
		print("Failed to Terminate")


def handshake(sock):
	i = 0
	while(True):
		try:
			sock.settimeout(TIMEOUT)
			sock.send('HSK*'.encode('utf-8'))
			packet, addr = sock.recvfrom(BUFFER_SIZE)
			decoded_packet = packet.decode('utf-8')
			if(decoded_packet[:4] == "HSK*"):
				response = decoded_packet[4:].split('<')
				sock.connect((response[1], int(response[2])))
				return sock
		except:
			if(i > 1):
				return False
		i += 1


class decoder:
	def __init__(self): 
		self.done= False
		self.image = False
		self.end = False

	def decode(self):
		return_val, video_image = VIDEO.read()
		if (not return_val):
			self.image = False
			self.done = True
			self.end = True
			return
		self.image = video_image
		self.done = True
		return
	
	def getImage(self):
		self.done = False
		return self.image

	def isDone(self):
		return self.done
		
	def getFilename(self):
		return self.filename
		
	def ended(self):
		return self.end


class encoder:
	def __init__(self, quality = 80):
		self.quality = quality
		self.encodedImage = False
		self.done = False
	
	def encode(self, image):
		if(image is False):
			self.done = True
			return
		gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		self.encodedImage = cv2.imencode('.jpg', gray, [int(cv2.IMWRITE_JPEG_QUALITY), self.quality])[1].tostring()
		self.done = True
		return

	def changeQuality(self, quality):
		self.quality = quality
		return

	def getImage(self):
		self.done = False
		return self.encodedImage

	def isDone(self):
		return self.done


class sender:
	def __init__(self, sock):
		self.sock = sock
		self.counter = 1
		self.done = False

	def send(self, encodedImage):
		self.done = False
		if(self.counter < 1):
			self.counter += 1
			self.done = True
			return
		self.counter = 1
		if(encodedImage is False):
			self.done = True
			return
		num_packets = "LEN*" + str(ceil((len(encodedImage)/BUFFER_SIZE)))
		try:
			self.sock.send(num_packets.encode('utf-8'))
			for i in range(int(len(encodedImage)/BUFFER_SIZE)+1):
				self.sock.send(encodedImage[i*BUFFER_SIZE:(i+1)*BUFFER_SIZE])
		except:
			print("Send Failure")
		self.done = True
		return

	def isDone(self):
		return self.done


class reciever:
	def __init__(self, sock):
		self.sock = sock
		self.response = ''
		self.connected = True
		self.updated = False
		self.stopped = True
		self.sock.settimeout(TIMEOUT)
		
	def start(self):
		self.stopped = False
		Thread(target=self.run, args=()).start()
		
	def stop(self):
		self.stopped = True
		
	def run(self):
		while(not self.stopped):
			try:
				reply, addr = self.sock.recvfrom(BUFFER_SIZE)
			except Exception as e:
				self.connected = False
				self.stopped = True
				print('Connection Timed Out')
				return
			decoded_reply = reply.decode('utf-8')
			if(decoded_reply[:4] == "FAC*"):
				self.response = decoded_reply[4:]
				self.updated = True
			elif(decoded_reply[:4] == "TER*"):
				self.connected = False
				self.stopped = True
				ter_code = decoded_reply[4:]
				print('Terminated with Code: ' + ter_code) 
				return
				
	def getResponse(self):
		n = self.updated
		self.updated = False
		return n, self.response
		
def runLocal():
	if(not VIDEO.isOpened()):
		print('Failed to open camera')
		return False
	cascade = cv2.CascadeClassifier("haarcascade_frontalface_default.xml")
	startTime = time.time()
	currentTime = time.time()
	while(time.time() - startTime < 20):
		prevTime = currentTime
		currentTime = time.time()
		framerate = 1/(currentTime-prevTime)
		return_val, video_image = VIDEO.read()
		if (not return_val):
			print("No Image from camera")
			return False
		greyImg = cv2.cvtColor(video_image, cv2.COLOR_BGR2GRAY)
		faces = cascade.detectMultiScale(greyImg, 1.3, 5)
		if(faces is not None):
			for(x,y,w,h) in faces:
				cv2.rectangle(video_image,(x,y),(x+w,y+h),(255,0,0),2)
		prop_val = cv2.getWindowProperty(CV_WINDOW_NAME, cv2.WND_PROP_ASPECT_RATIO)
		if(prop_val < 0.0):
			print('Closed')
			return False
		cv2.putText(video_image, "%.1f" % round(framerate,1), (1160,40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
		cv2.putText(video_image, "Running Locally", (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
		cv2.imshow(CV_WINDOW_NAME, video_image)
		cv2.waitKey(1)
	return True
		
def runClient(sock):
	p1 = decoder()
	p2 = encoder()
	p3 = sender(sock)
	p4 = reciever(sock)
	p4.start()
	cycleTime = []
	
	image = False
	prevImage = False
	doublePrevImage = False
	encodedImage = False
	response = ''
	
	cleaner = 0
	cv2.namedWindow(CV_WINDOW_NAME)
	startTime = time.time()
	currentTime = time.time()
	while(p4.connected and (time.time() - startTime < 20)):
		prevTime = currentTime
		currentTime = time.time()
		framerate = 1/(currentTime-prevTime)
		Thread(target=p1.decode, args=()).start()
		Thread(target=p2.encode, args=(image,)).start()
		Thread(target=p3.send, args=(encodedImage,)).start()
		triplePrevImage = doublePrevImage
		doublePrevImage = prevImage
		prevImage = image
		
		updated, response = p4.getResponse()
		faceParse = response.split("<")
		for substr in faceParse[1:]:
			coordParse = substr.split("|")
			x = int(coordParse[0])
			y = int(coordParse[1])
			w = int(coordParse[2])
			cv2.rectangle(triplePrevImage,(x,y),(x+w,y+w),(255,0,0),2)
		
		prop_val = cv2.getWindowProperty(CV_WINDOW_NAME, cv2.WND_PROP_ASPECT_RATIO)
		if(prop_val < 0.0):
			print("Closed")
			return False
		
		if(triplePrevImage is not False):
			cv2.putText(triplePrevImage, "Running with offloading", (10,40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
			cv2.putText(triplePrevImage, "%.1f" % round(framerate,1), (1160,40), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 2)
			cv2.imshow(CV_WINDOW_NAME, triplePrevImage)
			cv2.waitKey(1)
		if(p1.ended()):
			cleaner += 1
			if(cleaner > 3):
				break
		waitCycles = 0
		#p1.join()
		#p2.join()
		#p3.join()
		while((not p1.isDone()) or (not p2.isDone()) or (not p3.isDone())): # Remove after testing to ensure no hanging threads
			if( waitCycles > 2/CHECK_RATE):
				print("Hanging thread")
				print("p1: " + str(p1.isDone()))
				print("p2: " + str(p2.isDone()))
				print("p3: " + str(p3.isDone()))
				return False
			time.sleep(CHECK_RATE)
		image = p1.getImage()
		encodedImage = p2.getImage()
        		
		cycleTime.append(time.time() - startTime)
	p4.stop()
	
	return True
         
         
def main():
	
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	sock.connect((UDP_IP, UDP_PORT))
	sock = handshake(sock)
	if(sock is False):
		print('Failed to handshake')
		return
	sock.send(("DAT*"+str(time.time())+'<'+"0.25").encode("utf-8"))
	while(True):
		x = runClient(sock)
		if(x is False):
			break
		x = runLocal()
		if(x is False):
			break
	VIDEO.release()
	time.sleep(1)
	terminate(sock)
	sock.close()
	cv2.destroyAllWindows()
	print('Done')
    
    
    
if __name__ == "__main__":
    main()
