import bluetooth

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

    print("Waiting for connection on RFCOMM channel %d" % port)

    clientSocket, clientInfo = serverSocket.accept()
    print("Accepted connection from ", clientInfo)
    return clientSocket, serverSocket

def closeSockets(s, c):
    s.close()
    c.close()


def main():

    clientSocket, serverSocket = setupConnection()
    size = 1024

    try:
        while True:
            data = input('Type help for a list of commands\n>>')
            if(data == 'help'):
                print()

            elif(data == 'q'):
                print("Closing socket")
                closeSockets(serverSocket, clientSocket)
                quit()
            else:
                clientSocket.send(data)
                data = clientSocket.recv(size)
                if data:
                    print(data)
    except IOError:
        pass

    print("disconnected")
    closeSockets(serverSocket, clientSocket)
    print("all done")

if __name__ == "__main__":
    main()
