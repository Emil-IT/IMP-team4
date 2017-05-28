import bluetooth
import socket
import threading
import sys

HOST = "ctrl.gspd4.student.it.uu.se"
INETPORT = 8051
size = 1024

class RpiServerBT():
	"""docstring for RpiServerBT"""
	def __init__(self, parent):
		self.parent = parent
		serverBTSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		serverBTSocket.bind(("", bluetooth.PORT_ANY))
		serverBTSocket.listen(1)

		serverInetSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serverInetSocket.bind((HOST, INETPORT))
		serverInetSocket.listen(1)

		port = serverBTSocket.getsockname()[1]
		uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

		bluetooth.advertise_service(serverBTSocket, "rpiBluetoothServer",
						   service_id=uuid,
						   service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
						   profiles=[bluetooth.SERIAL_PORT_PROFILE],
							)
		bt = threading.Thread(target = self.socketConnection, args = (serverBTSocket, port))
		inet = threading.Thread(target = self.socketConnection, args = (serverInetSocket, INETPORT))
		#quit = threading.Thread(target = self.cleanExit, args = (serverInetSocket, serverBTSocket))

		bt.start()
		inet.start()
		#quit.start()

		bt.join()
		inet.join()
		#quit.join()

		serverInetSocket.close()
		serverBTSocket.close()
		for clinet in self.Parent.robotSockets:
			client[1].close()

	def socketConnection(self, serverSocket, port):
		try:
			while True:
				print("Waiting for connection on port %d" % port)
				clientSocket, clientInfo = serverSocket.accept()
				print("Accepted connection from ", clientInfo)
				clientSocket.sendall('Connected'.encode())
				robot_id = int(clientSocket.recv(size))
				print('Adding robot {} to list'.format(robot_id))
				self.parent.robotSockets.append((robot_id, clientSocket))
		finally:
			return


	def cleanExit(self, serverInetSocket, serverBTSocket):
		while True:
			if(input('Write quit for a clean exit:\n >>') == 'quit\n'):
				serverInetSocket.close()
				serverBTSocket.close()
				sys.exit('Server closed')
