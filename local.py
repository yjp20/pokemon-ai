"""
Local uses Pokemon-Showdown's simulate battle functionality to conduct a fight
locallay.
"""

import logging
import subprocess

logger = logging.getLogger("pokemon-ai.local")

class Local():
    """
    Local uses Pokemon-Showdown's simulate battle functionality to conduct a fight
    locallay.
    """
    def __init__(self, bot1, bot2, gamemode):
        args = ['thirdparty/Pokemon-Showdown/pokemon-showdown', 'simulate-battle']
        self.bot1 = bot1
        self.bot2 = bot2
        self.process = subprocess.Popen(
            args,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding='utf8')

        self.send('>start {"format-id": "%s"}' % gamemode)
        self.send('>player p1 {"name":"p1"}')
        self.send('>player p2 {"name":"p1"}')
        self.listener()
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait(timeout=0.2)

    def send(self, cmd):
        """ Send a message to the subprocess """
        self.process.stdin.write(cmd + '\n')
        self.process.stdin.flush()

    def listener(self):
        """ Listen for messages from the server """
        line = '\n'
        mode = 'both'
        while line:
            line = self.process.stdout.readline()
            if line == '\n':
                pass
            elif line == 'update\n':
                mode = 'both'
            elif line == 'sideupdate\n':
                player = self.process.stdout.readline()
                if player == 'p1\n':
                    mode = 'p1'
                if player == 'p2\n':
                    mode = 'p2'
            else:
                if mode == 'p1':
                    logger.debug(f'< p1 {line}')
                    self.bot1.read(line)
                if mode == 'p2':
                    logger.debug(f'< p2 {line}')
                    self.bot2.read(line)
                if mode == 'both':
                    logger.debug(f'< both {line}')
                    self.bot1.read(line)
                    self.bot2.read(line)
