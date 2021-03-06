import logging
from websocket_server import WebsocketServer

local = 'localhost'
pi = 'ctrl.gspd4.student.it.uu.se'
hosthome = '192.168.1.70'
class RpiServerWS():
    """docstring for WebsocketServer"""
    server = None
    def __init__(self, parent):
        self.parent = parent
        self.server = WebsocketServer(8050, host=hosthome, loglevel=logging.INFO)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_message_received(self.message_received)
        self.server.set_fn_client_left(self.client_left)
        print('Websocket Server started, waiting for clients to connect')
        self.server.run_forever()

    def new_client(self, client, server):
        #print('Connected by ', client)
        self.parent.clientSockets.append(client)
        greeting = '{"functionName":"connected", "args":{} }'
        self.server.send_message(client,greeting)

    def message_received(self, client, server, message):
        item = (message, self.server, client)
        #print('putting ', item, 'in the queue')
        self.parent.callbackQueue.put(item)
        #self.server.send_message(client, 'WS: Message put in queue')

    def client_left(self, client, server):
        self.parent.clientSockets.remove(client)
