import bluetooth
from _thread import start_new_thread

def setupConnection():
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

    
    return serverBTSocket, port

def closeSockets(s, c):
    s.close()
    c.close()
    
def CloseSockets(c):
    c.close()

def talkToClient(clientSocket, clientInfo):
    size = 1024
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


if __name__ == "__main__":
    serverBTSocket, port = setupConnection()
    while True:
        print("Waiting for connection on RFCOMM channel %d" % port)
        clientSocket, clientInfo = serverBTSocket.accept()
        print("Accepted connection from ", clientInfo)
        returnValue = talkToClient(clientSocket, clientInfo)
        #start_new_thread(talkToClient, (clientSocket, clientInfo))
        if(returnValue == -1):
            break
        

    serverBTSocket.close()