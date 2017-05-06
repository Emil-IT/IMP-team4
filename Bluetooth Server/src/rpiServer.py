# file: rfcomm-server.py
# auth: Albert Huang <albert@csail.mit.edu>
# desc: simple demonstration of a server application that uses RFCOMM sockets
#
# $Id: rfcomm-server.py 518 2007-08-10 07:20:07Z albert $

from bluetooth import *

serverSocket=BluetoothSocket( RFCOMM )
serverSocket.bind(("",PORT_ANY))
serverSocket.listen(1)

port = serverSocket.getsockname()[1]
size = 1024

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

advertise_service( serverSocket, "rpiBluetoothServer",
                   service_id = uuid,
                   service_classes = [ uuid, SERIAL_PORT_CLASS ],
                   profiles = [ SERIAL_PORT_PROFILE ], 
                    )

print("Waiting for connection on RFCOMM channel %d" % port)

clientSocket, clientInfo = serverSocket.accept()
print("Accepted connection from ", clientInfo)

try:
    while True:
        data = input('Write Something\n')
        if(data == 'q'):
            print("Closing socket")
            clientSocket.close()
            serverSocket.close()
            quit()
        clientSocket.send(data)
        data = clientSocket.recv(size)
        if data:
            print(data)
except IOError:
    pass

print("disconnected")

clientSocket.close()
serverSocket.close()
print("all done")