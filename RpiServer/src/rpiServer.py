import bluetooth
import threading
import asyncio
import datetime
import random
import websockets
import Decoder
import functions
import queue
from websocket_server import WebsocketServer
import logging

local = 'localhost'
pi = '130.243.201.239'
size = 1024
callbackQueue = queue.Queue()

class RpiServer(object):
    """docstring for ClassName"""
    server = None
    clientSockets = []
    robotSockets = []

    def __init__(self):
        ws = threading.Thread(target = self.setupBTConnection)
        bt = threading.Thread(target = self.setupWSConnection)

        ws.start()
        bt.start()
        print('threads started')
        self.listenToChildren()

        ws.join()
        bt.join()
        print('threads joined')


    def listenToChildren(self):
        while True:
            print('Ready to listen to children')
            try:
                item = callbackQueue.get()
                print('Doing work on task: ', item)
                if(hasattr(self, item[0])):
                    print('it exists')
                    getattr(self, item[0], None)(*tuple(item[1:]))
                    callbackQueue.task_done()
                else:
                    print('no such function')
            except queue.Empty:
                pass

    def redirectMessage(self, message, clientSocket, robotSocket):
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
            self.sendData(clientSocket, str(message))
        else:
            self.sendData(clientSocket, 'No robot connected :(')

    def sendData(self, client, message):
        self.server.send_message(client, message)

    def closeSockets(self, s, c):
        s.close()
        c.close()
        
    def CloseSockets(self, c):
        c.close()

    def talkToClient(seld, clientSocket, clientInfo):
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

    def setupWSConnection(self):
        self.server = WebsocketServer(1234, host=pi, loglevel=logging.INFO)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_message_received(self.message_received)
        self.server.set_fn_client_left(self.client_left)
        print('Websocket Server started, waiting for clients to connect')
        self.server.run_forever()

    def new_client(self, client, server):
        print('Connected by ', client)
        self.clientSockets.append(client)
        self.server.send_message_to_all("Hey all, a new client has joined us")

    def message_received(self, client, server, message):
        item = ('redirectMessage', message, client, 0)
        print('putting ', item, 'in the queue')
        callbackQueue.put(item)
        self.server.send_message(client, 'Message received')

    def client_left(self, client, server):
        self.clientSockets.remove(client)


    def setupBTConnection(self):
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
            self.robotSockets.append((clientInfo[0], clientSocket))
            print("Accepted connection from ", clientInfo)
            returnValue = self.talkToClient(clientSocket, clientInfo)
            if(returnValue == -1):
                break
        serverBTSocket.close()

if __name__ == "__main__":
    RpiServer()
    
