"""
Local uses Pokemon-Showdown's simulate battle functionality to conduct a fight
locally.
"""

from jinja2 import Template
import json
import copy
import logging
import subprocess
import lib.normalizer as normalizer

MODE_ALL = -1
LOGGER = logging.getLogger("pokemon-ai.local")


def handle(x):
    if isinstance(x, set):
        return list(x)
    return x.__dict__


class Local():
    """
    The Local class uses Pokemon-Showdown's simulate battle functionality to conduct a
    fight locally.

    Args:
        bot_list (list): List of Bots to compete in a Local simulator.
        gamemode (str): Format name of the gamemode to run in the local simulator.
        num (int): Number of simulations to run.
        save_replay (bool):
            Boolean value which determines whether or not to save the replay to
            'replay.html'.
    Attributes:
        process (subprocess.Local):
            The subprocess managing the showdown BattleStream using the
            official Pokemon-Showdown code in conjunction with the
            multirunner.js file used to run real battles.
        bots (list): List of Bots to compete in a Local simulator.
        save_replay (bool):
            Boolean value which determines whether or not to save the replay to
            'replay.html'.
        replay_log (list):
            List of the log of messages that were sent to all of the bots in
            the game which is then dumped to the replay.html file.
        bot_gamestates (list):
            Stores the deepcopy of each gamestate at every turn or half-turns
            where a swith is requested of a player.
        bot_norm(list):
            Similar to the bot_gamestates list, but contains the normalized versions of each of the 
    """
    def __init__(self, bot_list: list, gamemode: str, num: int, save_replay: bool):
        args = ['node', 'lib/multirunner.js', '2>/dev/null']

        if save_replay and num > 1:
            LOGGER.error("If saving replay, the number of simulations must be equal to 1")
            return

        self.process = subprocess.Popen(args,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE,
                                        stderr=subprocess.STDOUT,
                                        encoding='utf8')
        self.send(str(num))
        self.bots = [None]
        self.bots.extend(bot_list)
        self.save_replay = save_replay

        self.replay_log = []
        self.bot_gamestates = [None]
        self.bot_norm = [None]

        if save_replay:
            for i in range(1, len(self.bots)):
                self.bot_gamestates.append([])
                self.bot_norm.append([])

        while num > 0:
            line = self.process.stdout.readline()
            if line != "START\n":
                LOGGER.error("Something is wrong with the multirunner..?")
            self.send('>start {"formatid":"%s"}' % gamemode)
            for i in range(1, len(self.bots)):
                self.bots[i].new_gamestate()
                self.send('>player p%d {"name":"%s"}' % (i, self.bots[i].name))
            self.listener()
            LOGGER.info("FINISHED:" + str(num))
            num -= 1

        self.process.stdin.close()
        self.process.terminate()
        self.process.wait(timeout=0.2)

        if self.save_replay:
            data = dict()
            data["log"] = "".join(self.replay_log)
            for i in range(1, len(self.bots)):
                gamestate_str = json.dumps(self.bot_gamestates[i],
                                           default=handle,
                                           skipkeys=True)
                norm_str = json.dumps(self.bot_norm[i],
                                      default=handle,
                                      skipkeys=True)
                data["bot"+str(i)] = gamestate_str
                data["bot"+str(i)+"_norm"] = norm_str
            template_file = open("./web/replay.html.tmpl", "r")
            output_file = open("./replay.html", "w")
            template = Template("".join(template_file.readlines()))
            res = template.render(data)
            output_file.write(res)

    def send(self, cmd):
        """
        Send a message to self.subprocess then flushes output. Appends a
        newline if it doesn't already exist.

        Args:
            cmd (str): String to send to the subprocess.
        """
        LOGGER.info(cmd)
        if cmd[-1] != '\n':
            self.process.stdin.write(cmd + '\n')
        else:
            self.process.stdin.write(cmd)
        self.process.stdin.flush()

    def listener(self):
        """
        Listen for messages from self.subprocess and processes them to properly
        forward to the bots.
        """
        line = '\n'
        mode = MODE_ALL  # Any positive number corresponds to the user's idx
        while line:
            line = self.process.stdout.readline()
            msg = line.split("|")

            if line == '\n' and mode == MODE_ALL:
                # Shitty way of recognizing when to ask for a move.
                # I wish there was a better way, but the showdown
                # protocol was not designed with this in mind.

                LOGGER.debug("---- ASK MOVE ----")
                for i in range(1, len(self.bots)):
                    if self.save_replay:
                        ng = copy.deepcopy(self.bots[i].gamestate.__dict__())
                        self.bot_gamestates[i].append(ng)
                        self.bot_norm[i].append(normalizer.normalize(self.bots[i].gamestate, self.bots[i].gamestate.player_idx))
                    if self.bots[i].gamestate.result == -1 and not self.bots[i].gamestate.wait:
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
                    if len(msg) > 2 and msg[1] == 'split':
                        player_id = int(msg[2][1])
                        secret_line = self.process.stdout.readline()
                        public_line = self.process.stdout.readline()
                        LOGGER.info(f'<p{player_id} {secret_line[:-1]}')
                        LOGGER.info(f'<all {public_line[:-1]}')
                        for i in range(1, len(self.bots)):
                            self.bots[i].read(secret_line if player_id == i else public_line)
                        if self.save_replay:
                            self.replay_log.append(public_line)
                    else:
                        LOGGER.info(f'<all {line[:-1]}')
                        for i in range(1, len(self.bots)):
                            self.bots[i].read(line)
                        if self.save_replay:
                            self.replay_log.append(line)
