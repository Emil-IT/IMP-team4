import bluetooth
import threading
import queue
from websocket_server import WebsocketServer
import logging
import rpiServerWS
import rpiServerBT
import rpiServerARD
import select
import json
import sqlite3
import jsonBuilder


local = 'localhost'
pi = '130.243.201.239'
size = 1024

class RpiServer(object):
	"""docstring for ClassName"""
	server = None
	clientSockets = []
	robotSockets = []
	callbackQueue = queue.Queue()

	sensorJSON = ''
	databaseConn = sqlite3.connect('../db/warehouses.db')

	def __init__(self):
		ws = threading.Thread(target = self.setupBTConnection)
		bt = threading.Thread(target = self.setupWSConnection)
		ard = threading.Thread(target = self.setupARDConnection)

		ws.start()
		bt.start()
		ard.start()
		print('threads started')
		self.listenToChildren()

		ws.join()
		bt.join()
		ard.join()
		print('threads joined')


	def listenToChildren(self):
		while True:
			print('Ready to listen to children')
			try:
				item = self.callbackQueue.get()
				jsonData = item[0]
				print(jsonData)
				try:
					data = json.loads(jsonData)
					if(hasattr(self, data['functionName'])):
						print('Calling requested function')
						getattr(self, data['functionName'], None)(item[1], item[2], **(data['args']))
						self.callbackQueue.task_done()
					else:
						print('no such function')
				except (ValueError):
					print('Invalid json')
					pass # invalid json

			except queue.Empty:
				pass


	def get_data(self, wsServer, clientSocket):
		#zones
		zonesJSON = jsonBuilder.buildZones(self.databaseConn)
		
		robotsJSON = '"robots": []'
		
		
		warehouseJSON = '{'+zonesJSON+'}'
		print(warehouseJSON)
		self.sendData(wsServer, clientSocket, warehouseJSON)
		
		pass

	def pickUp(self, wsServer, clientSocket, **kwargs):
		self.issue_task(wsServer, clientSocket, shelfID = kwargs['shelfID'], pickUp = True)
		pass

	def dropOff(self, wsServer, clientSocket, **kwargs):
		self.issue_task(wsServer, clientSocket, shelfID = kwargs['shelfID'], pickUp = False)

	def issue_task(self, wsServer, clientSocket, **kwargs):
		if(len(self.robotSockets) == 0):
			if(kwargs['pickUp']):
				self.sendData(wsServer, clientSocket, '{"functionName": "pickUp", "errorMessage": "No robot connected :("}')
			else:
				self.sendData(wsServer, clientSocket, '{"functionName": "dropOff", "errorMessage": "No robot connected :("}')
			return
		robotSocket = self.robotSockets[int(kwargs['robotID'])][1]
		shelfCoords = self.getCoords(kwargs['shelfID'])
		path = self.getPath(shelfCoords, kwargs['pickUp'])
		try:
			ready_to_read, ready_to_write, in_error = \
			select.select([robotSocket,], [robotSocket,], [], 5)
		except select.error:
			robotSocket.shutdown(2)    # 0 = done receiving, 1 = done sending, 2 = both
			robotSocket.close()
		# connection error event here, maybe reconnect
			print('connection error')
			return
		if(len(ready_to_write) > 0):
			robotSocket.send(str(path).encode())
			print('Message sent to robot')
			response = robotSocket.recv(size)
			self.sendData(wsServer, clientSocket, response.decode())
			return
		else:
			robotSocket.close()
			robotSockets.pop(int(kwargs['robotID']))
		self.sendData(wsServer, clientSocket, 'Lost connection to robot')


	def getCoords(self, shelfID):
		shelfCoords = []
		section, shelf = list(shelfID)
		shelfCoords.append((ord(section) - 65) // 2)
		shelfCoords.append(int(shelf) // 2 + 1)
		shelfCoords.append((ord(section) - 65) % 2)
		shelfCoords.append(int(shelf) % 2)
		return shelfCoords

	def getPath(self, shelfCoords, pickUp):
		path = ['task']
		if(shelfCoords[0] > 0):
			path.append('right')
			for i in range(0, shelfCoords[0]):
				path.append('forward')
			path.append('left')
		for i in range(0, shelfCoords[1]):
			path.append('forward')
		if(shelfCoords[2] == 1):
			path.append('right')
		else:
			path.append('left')
		path.append('forward')
		for i in range(0, shelfCoords[3]):
			path.append('lift')
		if(pickUp):
			path.append('pick up')
		else:
			path.append('drop off')
		return path

	def redirectMessage(self, message, server, clientSocket, robotSocket):
		print('In redirect message')
		print('Connected robots :', self.robotSockets)
		if(len(self.robotSockets)>robotSocket):
			print('Sending ', message, ' to robot')
			self.robotSockets[robotSocket][1].send(message)
			data = self.robotSockets[robotSocket][1].recv(size)
			print('Recieved ', data, ' from robot')
			data = str(data).split('\'')[1].split('\\n')[0]
			message = "From robot: {}".format(data)
			print('Sending ', message, ' to client')
			self.sendData(server, clientSocket, str(message))
		else:
			self.sendData(server, clientSocket, 'No robot connected :(')



	def sendData(self, server, client, message):
		server.send_message(client, message)

	def setupWSConnection(self):
		rpiServerWS.RpiServerWS(self)

	def setupBTConnection(self):
		rpiServerBT.RpiServerBT(self)

	def setupARDConnection(self):
		rpiServerARD.RpiServerARD(self)



if __name__ == "__main__":
	RpiServer()

