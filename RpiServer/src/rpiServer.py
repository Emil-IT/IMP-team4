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
import time


local = 'localhost'
pi = '130.243.201.239'
size = 1024

class RpiServer(object):
	"""docstring for ClassName"""
	server = None
	clientSockets = []
	robotSockets = {}
	callbackQueue = queue.Queue()
	robotPositions = {}

	sensorJSON = ''
	databaseConn = sqlite3.connect('../db/warehouses.db')

	def __init__(self):
		ws = threading.Thread(target = self.setupBTConnection)
		bt = threading.Thread(target = self.setupWSConnection)
		ard = threading.Thread(target = self.setupARDConnection)
		#tsk = threading.Thread(target = self.taskHandler)

		ws.start()
		bt.start()
		ard.start()
		#tsk.start()
		print('threads started')
		self.listenToChildren()

		ws.join()
		bt.join()
		ard.join()
		#tsk.join()
		print('threads joined')


	def listenToChildren(self):
		while True:
			#print('Ready to listen to children')
			try:
				item = self.callbackQueue.get()
				jsonData = item[0]
				print(jsonData)
				try:
					data = json.loads(jsonData)
					if(hasattr(self, data['functionName'])):
						print('Calling requested function')
						t = threading.Thread(target = getattr(self, data['functionName'], None), args = (item[1], item[2]), kwargs = data['args'])
						t.start()
						#print('Hello from the main thread')
						self.callbackQueue.task_done()
					else:
						print('no such function')
				except (ValueError):
					print('Invalid json')
					pass # invalid json

			except queue.Empty:
				pass


	def get_data(self, wsServer, clientSocket):
		databaseConn = sqlite3.connect('../db/warehouses.db')
		#zones
		zonesJSON = jsonBuilder.buildZones(databaseConn)
		robotsJSON = jsonBuilder.buildRobots(databaseConn, self.robotPositions)
		packagesJSON = jsonBuilder.buildPackages(databaseConn)
		tasksJSON = jsonBuilder.buildTasks(databaseConn)
		warehouseJSON = '{'+zonesJSON+','+robotsJSON+','+packagesJSON+','+tasksJSON+'}'
		#print(warehouseJSON)
		response = '{"functionName":"get_data","args":'+warehouseJSON+'}'
		self.sendData(wsServer, clientSocket, response)
		pass

	def taskHandler(self):
		pass

	def issue_task(self, wsServer, clientSocket, **kwargs):
		databaseConn = sqlite3.connect('../db/warehouses.db')
		origin = kwargs['origin']
		destination = kwargs['destination']
		zone = kwargs['zone']
		priority = kwargs.get('priority', 3)
		robot_id = ""
		package_id = ""
		task_id = ""
		returnJson = {"functionName": "issue_task", "args": {}}
		returnJson["args"]["origin"] = origin
		returnJson["args"]["destination"] = destination
		returnJson["args"]["zone"] = zone
		returnJson["args"]["task_id"] = task_id
		returnJson["args"]["package_id"] = package_id
		returnJson["args"]["robot_id"] = robot_id
		returnJson["args"]["priority"] = priority
		if(len(self.robotSockets) == 0):
			self.sendData(wsServer, clientSocket, json.dumps(returnJson))
			return
		c = databaseConn.cursor()
		print('Fetching robot_id form db zone:{}'.format(zone))
		query = "select robot_id from zone, warehouse where zone.warehouse_id = warehouse.id and warehouse.site = 'uppsala' and zone.position = {}".format(zone)
		print('executiong query: {}'.format(query))
		c.execute(query)
		print('query done')
		robot_id = c.fetchone()[0]
		print('robot_id: ', robot_id)
		if(robot_id == None):
			print('No robot in zone {}'.format(zone))
			self.sendData(wsServer, clientSocket, json.dumps(returnJson))
			return
		returnJson["args"]["robot_id"] = robot_id
		returnJson["args"]["task_id"] = str(uuid.uuid4())
		print('Added ids')
		if(origin == "conv"):
			returnJson["args"]["package_id"] = str(uuid.uuid4())
		else:
			print('Fetching package ID')
			query = "select package_id from shelf, warehouse where shelf.warehouse_id = warehouse.id and warehouse.site = 'uppsala' and shelf.name = '{}'".format(str(origin))
			print('executing query: {}'.format(query))
			c.execute(query)
			print('Package ID fetched')
			package_id = c.fetchone()[0]
			returnJson["args"]["package_id"] = package_id
		self.sendData(wsServer, clientSocket, json.dumps(returnJson))

		#print(self.robotSockets)
		robotSocket = self.robotSockets[int(robot_id)]
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
			for square in self.getIntersections(shelfCoords):
				print('Pos: ', square)
				response = robotSocket.recv(size)
				self.robotPositions[robot_id] = square

			#self.sendData(wsServer, clientSocket, ('From robot' + response.decode()))
			print('Task_done')
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
				path.append('FF')
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
				path.append('FF')
			path.append('L')
		if(pickUp):
			path.append('d')
		path.append('S')
		path.append('I')
		return ''.join(path)

	def getIntersections(self, shelfCoords):
		intersections = []
		pointer = 0
		for i in range(0,shelfCoords[0]):
			pointer += 10
			intersections.append(pointer)
			pointer += 1
			intersections.append(pointer)
		pointer += 1
		intersections.append(pointer)
		for i in range(1, shelfCoords[1]):
			pointer += 3
			intersections.append(pointer)
		intersections.append(pointer + shelfCoords[2]+1)
		intersections.append(pointer)
		for i in range(1,shelfCoords[1]):
			pointer -= 3
			intersections.append(pointer)
		pointer -= 1
		intersections.append(pointer)
		for i in range(0,shelfCoords[0]):
			pointer -= 1
			intersections.append(pointer)
			pointer -= 10
			intersections.append(pointer)
		return intersections

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

