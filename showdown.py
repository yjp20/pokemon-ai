#!/bin/python3

"""
Uses a selected Bot class to compete within the official Showdown server
"""

import asyncio
import random
import string
import requests as requests
import websockets as ws

WS_URI = 'ws://localhost:8000/showdown/websocket'
HTTP_URI = 'http://play.pokemonshowdown.com/~~localhost/action.php'

class Showdown():
    """
    Uses a selected Bot class to compete within the official Showdown server
    """
    def __init__(self, ws_uri, http_uri):
        self.ws_uri = ws_uri
        self.http_uri = http_uri
        self.name = ''.join([random.choice(string.ascii_letters) for n in range(18)])
        self.sock = None
        self.challstr = None

        asyncio.get_event_loop().run_until_complete(
            self.init_stream()
        )

    async def init_stream(self):
        """
        Initializes Pokemon showdown websocket stream, then calls
        Showdown.handle_msg() to manage the messages sent to the client by the
        server.
        """
        async with ws.connect(self.ws_uri) as sock:
            self.sock = sock
            await sock.send("|/autojoin")
            while True:
                msg = await sock.recv()
                for line in msg.split('\n'):
                    await self.handle_msg(line)

    async def handle_msg(self, msg):
        """
        Handles message, `msg` which is then processed by the corresponding if
        statement.

        Args
            msg: string that contains the websocket message from the
            Pokemon-Showdown server to this client
        """

        print('RECV')
        msg = msg.split('|')

        if len(msg) < 2 or msg[1] == '':
            pass
        elif msg[1] == 'customgroups':
            pass
        elif msg[1] == 'formats':
            pass
        elif msg[1] == 'j':
            pass

        elif msg[1] == 'updateuser':
            print(msg[2], self.name)
            if msg[2] != self.name:
                # first guest username, hasn't logged in yet
                print('skip')
            else:
                print('not skip')
                # start searching for matches
                await self.sock.send('|/utm null')
                await self.sock.send('|/challenge dsfefefad,gen7randombattle')
                # await self.sock.send('|/search gen7randombattle')

        elif msg[1] == 'challstr':
            # login into server without password
            # bots don't need security :)
            self.challstr = f'{msg[2]}|{msg[3]}'
            payload = {
                'act': 'getassertion',
                'userid': self.name,
                'challstr': self.challstr,
                }

            res = requests.post(self.http_uri, data=payload)
            await self.sock.send(f'|/trn {self.name},0,{res.text}')
        else:
            # TOOD:
            print(msg)
