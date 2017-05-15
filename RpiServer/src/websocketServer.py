#!/usr/bin/env python

import asyncio
import datetime
import random
import websockets
import Decoder
import functions

local = 'localhost'
pi = '130.243.201.239'

# @asyncio.coroutine
# def time(websocket, path):
    # print(path)
    # now = datetime.datetime.utcnow().isoformat() + 'Z'
    # yield from websocket.send(now)
    # yield from asyncio.sleep(random.random() * 3)

@asyncio.coroutine
def hello(websocket, path):
    print('hi')
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
        greeting = "Hello {}!".format(name)
        yield from websocket.send(str(greeting))
        print("> {}".format(greeting))


if __name__ == '__main__':
    start_server = websockets.serve(hello, local, 1234)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
    