"""
Local uses Pokemon-Showdown's simulate battle functionality to conduct a fight
localy.
"""

import json
import logging
import subprocess

MODE_ALL = -1
LOGGER = logging.getLogger("pokemon-ai.local")


class Local():
    """
    Local uses Pokemon-Showdown's simulate battle functionality to conduct a fight
    localy.
    """
    def __init__(self, bot_list, gamemode, num):
        args = ['/bin/node', 'multirunner.js', '2>/dev/null']
        self.process = subprocess.Popen(args,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        encoding='utf8')
        self.send(str(num))
        self.bots = [None]
        self.bots.extend(bot_list)
        while num > 0:
            line = self.process.stdout.readline()
            if line != "START\n":
                LOGGER.error("huh?")
            self.send('>start {"formatid":"%s"}' % gamemode)
            for i in range(1, len(self.bots)):
                self.bots[i].new_gamestate()
                self.send('>player p%d {"name":"%s"}' % (i, self.bots[i].name))
            self.listener()
            print("FINISHED:" + str(num))
            num -= 1
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait(timeout=0.2)

    def send(self, cmd):
        """ Send a message to self.subprocess """
        LOGGER.info(cmd)
        if cmd[-1] != '\n':
            self.process.stdin.write(cmd + '\n')
        else:
            self.process.stdin.write(cmd)
        self.process.stdin.flush()

    def listener(self):
        """ Listen for messages from self.subprocess """
        line = '\n'
        mode = MODE_ALL  # Any positive number corresponds to the user s.t. 2 => p2
        while line:
            line = self.process.stdout.readline()
            msg = line.split('|')

            if line == '\n' and mode == MODE_ALL:
                # Shitty way of recognizing when to ask for a move from the bots
                LOGGER.debug("---- ASK MOVE ----")
                for i in range(1, len(self.bots)):
                    if self.bots[i].gamestate.result == -1 and not self.bots[
                            i].gamestate.wait:
                        choice = self.bots[i].choose()
                        if choice is not None:
                            choice_str = f'>p{i} {choice}'
                            self.send(choice_str)

            elif line == 'update\n':
                mode = MODE_ALL

            elif line == 'sideupdate\n':
                player = self.process.stdout.readline()
                mode = int(player[1])  # takes out 2 from p2

            elif line == 'end\n':
                result = self.process.stdout.readline()
                result_json = json.loads(result)
                LOGGER.debug(json.dumps(result_json, indent=True))
                while line.strip() != "END":
                    line = self.process.stdout.readline()
                self.send("\x04")
                return

            elif line != '\n':
                if mode != MODE_ALL:
                    LOGGER.info(f'<p{mode} {line[:-1]}')
                    self.bots[mode].read(line)
                else:
                    LOGGER.info(f'<all {line[:-1]}')
                    if len(msg) > 2 and msg[1] == 'split':
                        player_id = int(msg[2][1])
                        secret_line = self.process.stdout.readline()
                        public_line = self.process.stdout.readline()
                        LOGGER.info(f'<p{player_id} {secret_line[:-1]}')
                        LOGGER.info(f'<all {public_line[:-1]}')
                        for i in range(1, len(self.bots)):
                            self.bots[i].read(secret_line if player_id ==
                                              i else public_line)
                    else:
                        for i in range(1, len(self.bots)):
                            self.bots[i].read(line)
