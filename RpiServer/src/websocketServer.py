import rpiServer
import logging

local = 'localhost'
pi = '130.243.201.239'

class WebsocketServer():
    """docstring for WebsocketServer"""
    server = None
    def __init__(self, parent):
        self.server = WebsocketServer(1234, host=pi, loglevel=logging.INFO)
        self.server.set_fn_new_client(self.new_client)
        self.server.set_fn_message_received(self.message_received)
        self.server.set_fn_client_left(self.client_left)
        print('Websocket Server started, waiting for clients to connect')
        self.server.run_forever()
        
    def new_client(self, client, server):
        print('Connected by ', client)
        parent.clientSockets.append(client)
        self.server.send_message_to_all("Hey all, a new client has joined us")

    def message_received(self, client, server, message):
        item = ('redirectMessage', message, client, 0)
        print('putting ', item, 'in the queue')
        parent.callbackQueue.put(item)
        self.server.send_message(client, 'Message received')

    def client_left(self, client, server):
        parent.clientSockets.remove(client)
