"""
Local uses Pokemon-Showdown's simulate battle functionality to conduct a fight
locallay.
"""

import subprocess

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

        # start battle
        self.send('>start {"format-id": "%s"}' % gamemode)
        self.send('>player p1 {"name":"p1"}')
        self.send('>player p2 {"name":"p1"}')

        # process lines continually
        self.listener()

        # terminate after done
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait(timeout=0.2)

    def send(self, cmd):
        self.process.stdin.write(cmd + '\n')
        self.process.stdin.flush()

    def listener(self):
        line = self.process.stdout.readline()
        mode = ''
        while line:
            if line == 'update\n':
                mode = 'all'
            elif line == 'sideupdate\n':
                pass
            elif line == 'p1\n':
                mode = 'p1'
            elif line == 'p2\n':
                mode = 'p2'
            else:
                if mode == 'all':
                    self.bot1.read(line)
                    self.bot2.read(line)
                elif mode == 'p1':
                    self.bot1.read(line)
                elif mode == 'p2':
                    self.bot2.read(line)
            line = self.process.stdout.readline()
