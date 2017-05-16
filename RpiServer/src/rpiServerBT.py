import bluetooth

class RpiServerBT():
    """docstring for RpiServerBT"""
    def __init__(self, parent):
        self.parent = parent
        serverBTSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        serverBTSocket.bind(("", bluetooth.PORT_ANY))
        serverBTSocket.listen(1)

        port = serverBTSocket.getsockname()[1]
        uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

        bluetooth.advertise_service(serverBTSocket, "rpiBluetoothServer",
                           service_id=uuid,
                           service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                           profiles=[bluetooth.SERIAL_PORT_PROFILE],
                            )
        while True:
            print("Waiting for connection on RFCOMM channel %d" % port)
            clientSocket, clientInfo = serverBTSocket.accept()
            self.parent.robotSockets.append((clientInfo[0], clientSocket))
            print("Accepted connection from ", clientInfo)
            returnValue = self.talkToClient(clientSocket, clientInfo)
            if(returnValue == -1):
                break
        serverBTSocket.close()

    def talkToClient(self, clientSocket, clientInfo):
        try:
            print('Type help for a list of commands\n')
            while True:
                data = input('>>')
                if(data == 'help'):
                    print()

                elif(data == 'q'):
                    clientSocket.send(data)
                    print("Closing  client and server sockets")
                    clientSocket.close()
                    return -1
                else:
                    clientSocket.send(data)
                    data = clientSocket.recv(size)
                    if data:
                        print(data)
        except IOError:
            pass

        print("disconnected")
        clientSocket.close()
        print("all done")
        return

    def closeSockets(self, s, c):
        s.close()
        c.close()
        
    def CloseSockets(self, c):
        c.close()

		