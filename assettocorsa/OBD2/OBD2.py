import socket
import threading
import json
import sys
import os
import platform
import ac
import acsys

# Importing files to access assetto shared memory
# ------------------------------------------------------
if platform.architecture()[0] == "64bit":
  sysdir = "stdlib64"
else:
  sysdir = "stdlib"

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'lib', sysdir))
os.environ['PATH'] = os.environ['PATH'] + ";."

from sim_info import info


# Constants
# ------------------------------------------------------
SERVER_HOST = socket.gethostbyname(socket.gethostname())
PORT = 8165
HEADER_SIZE = 64
ENCODING = 'utf-8'
BASE_ALT = 250 # metres 


# Getting Assetto Corsa data
# ------------------------------------------------------
class OBD:
	def __init__(self):
		self.commands = {
			'12': self.getRPM,
			'13': self.getSpeed,
			'17': self.getThrottlePos,
			'47': self.getFuelLevel,
			'51': self.getBaroPressure
		}

	def supports(self, pid):
		return pid in self.commands

	def query(self, pid):
		return self.commands[pid]()

	def getRPM(self):
		return round(ac.getCarState(0, acsys.CS.RPM), 2)

	def getSpeed(self):
		return round(ac.getCarState(0, acsys.CS.SpeedKMH), 2)
	
	def getThrottlePos(self):
		return round(ac.getCarState(0, acsys.CS.Gas), 2) * 100

	def getFuelLevel(self):
		return round((info.physics.fuel / info.static.maxFuel) * 100, 2)

	def getBaroPressure(self):
		# 1 in-game unit = 1 metre
		yPos = ac.getCarState(0, acsys.CS.WorldPosition)[1]
		altitude = BASE_ALT + yPos
		return round(((44330.8 - altitude) / 4946.54) ** (1 / 0.1902632), 2)


# Emulation Server
# ------------------------------------------------------
class EmulationServer:
	listening = False
	connected = False

	def __init__(self):
		self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.server.bind((SERVER_HOST, PORT))
		self.server.listen(1)
 
		# Listen on seperate thread to prevent blocking
		self.listening = True
		thread = threading.Thread(target=self.listen)
		thread.start()


	# Sending and receiving socket messages
	# -------------------------------------------------------------------------
	def recv(self):
		msgLen = self.clientConn.recv(HEADER_SIZE).decode(ENCODING)
		if not msgLen: return

		msgLen = int(msgLen)
		msg = self.clientConn.recv(msgLen).decode(ENCODING)
		return msg

	def send(self, data):
		msg = json.dumps(data).encode(ENCODING)
		msgLen = len(msg)

		header = str(msgLen).encode(ENCODING)
		header += b' ' * (HEADER_SIZE - len(header))

		self.clientConn.send(header)
		self.clientConn.send(msg)


	# Listening for clients
	# -------------------------------------------------------------------------
	def listen(self):
		while self.listening:
			self.clientConn, self.clientAddr = self.server.accept()

			# Handle Client
			self.connected = True
			while self.connected:
				msg = self.recv()

				if msg == '!disconnect':
					self.connected = False
				elif obd.supports(msg):
					self.send(obd.query(msg))
				else:
					self.send('unsupported')

			self.clientConn.close()

	def shutdown(self):
		self.listening = False
		self.connected = False



# Assetto Corsa hooks
# ------------------------------------------------------
obd = OBD()
server = None

def acMain(acVersion):
	global server
	appWindow = ac.newApp("OBD2")
	ac.setSize(appWindow, 200, 200)
	ac.console("OBD2 Launched")

	server = EmulationServer()
	ac.console("Server Ready")

	return "OBD2"

# Must be included or the app becomes blocked
def acUpdate(deltaT):
	pass

def acShutdown():
	global server
	server.shutdown()
