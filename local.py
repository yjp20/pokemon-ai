"""
Local uses Pokemon-Showdown's simulate battle functionality to conduct a fight
locallay.
"""

import json
import logging
import subprocess

MODE_ALL = -1
LOGGER = logging.getLogger("pokemon-ai.local")

class Local():
    """
    Local uses Pokemon-Showdown's simulate battle functionality to conduct a fight
    locallay.
    """
    def __init__(self, bot_list, gamemode):
        args = ['thirdparty/Pokemon-Showdown/pokemon-showdown', 'simulate-battle']
        self.bots = [None] # bot numbers start from 1, so 0 index => None
        self.bots.extend(bot_list)
        self.process = subprocess.Popen(args,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        encoding='utf8')
        self.send('>start {"format-id": "%s"}' % gamemode)
        for i in range(1, len(self.bots)):
            self.send('>player p%d {"name":"%s"}' % (i, self.bots[i].name))
        self.listener()
        self.process.stdin.close()
        self.process.terminate()
        self.process.wait(timeout=0.2)

    def send(self, cmd):
        """ Send a message to self.subprocess """
        LOGGER.info(cmd)
        self.process.stdin.write(cmd + '\n')
        self.process.stdin.flush()

    def listener(self):
        """ Listen for messages from self.subprocess """
        line = '\n'
        mode = MODE_ALL # Any positive number corresponds to the user s.t. 2 => p2
        while line:
            line = self.process.stdout.readline()
            msg = line.split('|')

            if line == '\n':
                if mode == MODE_ALL:    # Hacky way to indicate the end of the simulator output
                    for i in range(1, len(self.bots)):
                        choice = self.bots[i].choose()
                        if choice != None:
                            choice_str = f'>p{i} {choice}'
                            self.send(choice_str)

            elif line == 'update\n':
                mode = MODE_ALL

            elif line == 'sideupdate\n':
                player = self.process.stdout.readline()
                mode = int(player[1]) # takes out 2 from p2

            elif line == 'end\n':
                result = self.process.stdout.readline()
                result_json = json.loads(result)
                LOGGER.debug(json.dumps(result_json, indent=True))
                return

            else:
                if mode == MODE_ALL:
                    LOGGER.info(f'<all {line[:-1]}')
                    if len(msg) > 2 and msg[1] == 'split':
                        player_id = int(msg[2][1])
                        secret_line = self.process.stdout.readline()
                        public_line = self.process.stdout.readline()
                        LOGGER.info(f'<p{player_id} SECRET: {secret_line[:-1]}')
                        LOGGER.info(f'<all PUBLIC: {public_line[:-1]}')
                        for i in range(1, len(self.bots)):
                            self.bots[i].read(secret_line if player_id == i else public_line)
                    else:
                        for i in range(1, len(self.bots)):
                            self.bots[i].read(line)
                else:
                    LOGGER.info(f'<p{mode} {line[:-1]}')
                    self.bots[mode].read(line)
