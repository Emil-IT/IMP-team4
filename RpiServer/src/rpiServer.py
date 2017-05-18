import bluetooth
import threading
import queue
from websocket_server import WebsocketServer
import logging
import rpiServerWS
import rpiServerBT
import rpiServerARD

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
                print('Doing work on task: ', item)
                if(hasattr(self, item[0])):
                    print('it exists')
                    getattr(self, item[0], None)(*tuple(item[1:]))
                    self.callbackQueue.task_done()
                else:
                    print('no such function')
            except queue.Empty:
                pass

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
    
