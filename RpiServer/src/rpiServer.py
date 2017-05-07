import bluetooth
from _thread import start_new_thread

def setupConnection():
    serverSocket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    serverSocket.bind(("", bluetooth.PORT_ANY))
    serverSocket.listen(1)

    port = serverSocket.getsockname()[1]


    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

    bluetooth.advertise_service(serverSocket, "rpiBluetoothServer",
                       service_id=uuid,
                       service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                       profiles=[bluetooth.SERIAL_PORT_PROFILE],
                        )

    
    return serverSocket, port

def closeSockets(s, c):
    s.close()
    c.close()
    
def CloseSockets(c):
    c.close()

def talkToClient():
    size = 1024
    try:
        print('Type help for a list of commands\n')
        while True:
            data = input('>>')
            if(data == 'help'):
                print()

            elif(data == 'q'):
                clientSocket.send(data)
                print("Closing socket")
                clientSocket.close()
                return
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
    serverSocket, port = setupConnection()
    while True:
        print("Waiting for connection on RFCOMM channel %d" % port)
        clientSocket, clientInfo = serverSocket.accept()
        print("Accepted connection from ", clientInfo)
        start_new_thread(talkToClient, (clientSocket, clientInfo))

    serverSocket.close()