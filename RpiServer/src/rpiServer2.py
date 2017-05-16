import bluetooth
import threading
import websocketServer
import asyncio
import datetime
import random
import websockets
import Decoder
import functions
import queue

local = 'localhost'
pi = '130.243.201.239'
callbackQueue = queue.Queue()

class RpiServer(object):
    """docstring for ClassName"""

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
                    getattr(self, item[0], None)(*tuple(item[1:]))
                    callbackQueue.task_done()
                else:
                    print('no such function')
            except queue.Empty:
                pass

    def redirectMessage(self, message, clientSocket, robotSocket):
        print('In redirect message')
        print('Connected robots :', self.robotSockets)
        print(message, clientSocket, robotSocket)


    def closeSockets(self, s, c):
        s.close()
        c.close()
        
    def CloseSockets(self, c):
        c.close()

    def talkToClient(seld, clientSocket, clientInfo):
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

    def setupWSConnection(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start_server = websockets.serve(self.hello, pi, 1234)
        asyncio.get_event_loop().run_until_complete(start_server)
        asyncio.get_event_loop().run_forever()

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

    @asyncio.coroutine
    def hello(self, websocket, path):
        print('Connected by ', websocket)
        function, argList = Decoder.Decoder.decode(path)
        print('function=' + function)
        print('arguments=' + str(argList))
        if argList is None:
            argList = []
        if(hasattr(functions.Functions, function)):
            greeting = getattr(functions.Functions, function)(*tuple([val[1] for val in argList]))
        else:
            greeting = 'No such function'
        
        #name = yield from websocket.recv()
        #print("< {}".format(name))

        #greeting = "Hello {}!".format(name)
        print('Greeting='+str(greeting))
        yield from websocket.send(str(greeting))
        #print("> {}".format(greeting))
        while True:
            name = yield from websocket.recv()
            print("< {}".format(name))
            item = ('redirectMessage', name, websocket, 0)
            print('putting ', item, 'in the queue')
            callbackQueue.put(item)
            greeting = "Hello {}!".format(name)
            yield from websocket.send(str(greeting))
            print("> {}".format(greeting))

    


if __name__ == "__main__":
    RpiServer()
    
