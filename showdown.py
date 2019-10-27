#!/bin/python3

"""
Uses a selected Bot class to compete within the official Showdown server
"""

import asyncio
import random
import string
import requests as requests
import websockets as ws

WS_URI = 'ws://sim.smogon.com:8000/showdown/websocket'
HTTP_URI = 'http://play.pokemonshowdown.com/action.php'

def random_name():
    """ Returns a 18 character long random username of ascii letters """
    return ''.join([random.choice(string.ascii_letters) for n in range(18)])

class Showdown():
    """ Uses a selected Bot class to compete within the official Showdown server """
    def __init__(self, bot, **kwargs):
        self.bot = bot
        self.ws_uri = kwargs.get("ws_uri", WS_URI)
        self.http_uri = kwargs.get("http_uri", HTTP_URI)
        self.name = kwargs.get("name", random_name())
        self.challenge = kwargs.get("challenge", None)
        self.gamemode = kwargs.get("gamemode", "gen1randombattle")
        self.sock = None
        self.challstr = None
        self.on_login = None

        if self.challenge:
            self.on_login = self.challenge_user
        else:
            self.on_login = self.auto_find

        asyncio.get_event_loop().run_until_complete(
            self.init_stream()
        )

    def challenge_user(self):
        """ Challenges specified user in self.challenge """
        self.sock.send()

    def auto_find(self):
        """ auto joins selected gamemode """
        self.sock.send(f'|/search {self.gamemode}')

    async def init_stream(self):
        """
        Initializes Pokemon showdown websocket stream, then calls
        Showdown.handle_msg() to manage the messages sent to the client by the
        server
        """
        async with ws.connect(self.ws_uri) as sock:
            self.sock = sock
            self.sock.send('|/autojoin')
            while True:
                msg = await sock.recv()
                for line in msg.split('\n'):
                    await self.handle_msg(line)

    async def handle_msg(self, msg):
        """
        Handles message, `msg` which is then processed by the corresponding if
        statements.

        Args
            msg: string that contains the websocket message from the
            Pokemon-Showdown server to this client
        """
        msg = msg.split('|')
        ignore_msg = ['', 'customgroups', 'formats', 'j']
        if len(msg) < 2 or msg[1] in ignore_msg:
            return
        elif msg[1] == 'challstr':
            self.challstr = f'{msg[2]}|{msg[3]}'
            payload = {
                'act': 'getassertion',
                'userid': self.name,
                'challstr': self.challstr,
                }
            res = requests.post(self.http_uri, data=payload)
            await self.sock.send(f'|/trn {self.name},0,{res.text}')
        elif msg[1] == 'updateuser':
            if msg[2] == self.name:
                await self.sock.send('|/utm null')
                await self.on_login()
        else:
            print(f'Unhandled command {msg}')
