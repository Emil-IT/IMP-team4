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
import uuid


local = 'localhost'
pi = '130.243.201.239'
size = 1024

class RpiServer(object):
	"""docstring for ClassName"""
	server = None
	clientSockets = []
	robotSockets = []
	callbackQueue = queue.Queue()
	robotPositions = []

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
		robotsJSON = jsonBuilder.buildRobots(self.databaseConn, self.robotPositions)
		packagesJSON = jsonBuilder.buildPackages(self.databaseConn)
		tasksJSON = jsonBuilder.buildTasks(self.databaseConn)
		warehouseJSON = '{'+zonesJSON+','+robotsJSON+','+packagesJSON+','+tasksJSON+'}'
		#print(warehouseJSON)
		response = '{"functionName":"get_data","args":'+warehouseJSON+'}'
		self.sendData(wsServer, clientSocket, response)
		pass

	def issue_task(self, wsServer, clientSocket, **kwargs):
		origin = kwargs['origin']
		destination = kwargs['destination']
		zone = kwargs['zone']
		robot_id = ""
		package_id = ""
		task_id = ""
		priority = 0
		returnJson = {"functionName": "issue_task", "args": {}}
		returnJson["args"]["origin"] = origin
		returnJson["args"]["destination"] = destination
		returnJson["args"]["zone"] = zone
		returnJson["args"]["task_id"] = task_id
		returnJson["args"]["package_id"] = package_id
		returnJson["args"]["robot_id"] = robot_id
		returnJson["args"]["priority"] = priority
		if(len(self.robotSockets) == 0):
			self.sendData(wsServer, clientSocket, str(returnJson))
			return
		c = self.databaseConn.cursor()
		print('Fetching robot_id form db zone:{}'.format(zone))
		query = "select robot_id from zone, warehouse where zone.warehouse_id = warehouse.id and warehouse.site = 'uppsala' and zone.position = {}".format(zone)
		print('executiong query: {}'.format(query))
		c.execute(query)
		print('query done')
		robot_id = c.fetchone()[0]
		print('robot_id: ', robot_id)
		if(robot_id == None):
			print('No robot in zone {}'.format(zone))
			self.sendData(wsServer, clientSocket, str(returnJson))
			return
		returnJson["args"]["robot_id"] = robot_id
		returnJson["args"]["task_id"] = uuid.uuid4()
		print('Added ids')
		if(origin == "conv"):
			returnJson["args"]["package_id"] = uuid.uuid4()
		else:
			print('Fetching package ID')
			query = "select package_id from shelf, warehouse where shelf.warehouse_id = warehouse.id and warehouse.site = 'uppsala' and shelf.name = '{}'".format(str(origin))
			print('executing query: {}'.format(query))
			c.execute(query)
			print('Package ID fetched')
			package_id = c.fetchone()[0]
			returnJson["args"]["package_id"] = package_id
		self.sendData(wsServer, clientSocket, str(returnJson))

		robotSocket = self.robotSockets[int(robot_id)][1]
		if(origin == 'conv'):
			shelf = destination
			pickUp = 0
		elif(destination == 'conv'):
			shelf = origin
			pickUp = 1
		else:
			pass #Not yet implemented
		shelfCoords = self.getCoords(shelf)
		path = self.getPath(shelfCoords, pickUp)
		print(path)
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
			self.sendData(wsServer, clientSocket, ('From robot' + response.decode()))
			return
		else:
			robotSocket.close()
			robotSockets.pop(int(robot_id))
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
		path = []
		if(not pickUp):
			path.append('S')
			path.append('P')
			path.append('S')
		if(shelfCoords[0] > 0):
			path.append('R')
			for i in range(0, shelfCoords[0]):
				path.append('F')
			path.append('L')
		for i in range(0, shelfCoords[1]):
			path.append('F')
		if(shelfCoords[2] == 1):
			path.append('R')
		else:
			path.append('L')
		path.append('F')
		for i in range(0, shelfCoords[3]):
			path.append('U')
		if(pickUp):
			path.append('P')
		else:
			path.append('d')
		path.append('S')
		path.append('I')
		for i in range(0, shelfCoords[3]):
			path.append('D')
		path.append('F')
		if(shelfCoords[2] == 0):
			path.append('R')
		else:
			path.append('L')
		for i in range(0, shelfCoords[1]):
			path.append('F')
		if(shelfCoords[0] > 0):
			path.append('R')
			for i in range(0, shelfCoords[0]):
				path.append('F')
			path.append('L')
		if(pickUp):
			path.append('d')
		path.append('S')
		path.append('I')
		return ''.join(path)

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
		try:
			server.send_message(client, message)
		except BrokenPipeError:
				print("Socket was closed")
				pass

	def setupWSConnection(self):
		rpiServerWS.RpiServerWS(self)

	def setupBTConnection(self):
		rpiServerBT.RpiServerBT(self)

	def setupARDConnection(self):
		rpiServerARD.RpiServerARD(self)


if __name__ == "__main__":
	RpiServer()

