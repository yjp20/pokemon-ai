"""
This module reads and stores GameState, then uses the Bot Class to then act on
that GameState.
"""

import json
import importlib

class GameState():
    """
    Stores gamestate as GameState.state, which is then used by the bot. This
    class also normalizes data to be used in ML purposes.
    """
    def __init__(self):
        self.state = {}

    def parse(self, state, normalize):
        """
        Takes in the state then processes it if ML, or copies it to state
        depending on needs.

        Args:
            state: state JSON string from Pokemon-Showdown
            normalize: whether or not to normalize data for ML
        """
        if normalize:
            pass
        else:
            self.state = json.loads(state)

class Bot():
    """
    Bot that tkes in state message from Pokemon-Showdown and makes decisions
    based on that state information.
    """
    def __init__(self, name, gen, bot_type, verbose):
        """
        Bot class initializer.

        Args:
            name: string of the name of the bot
            bot_type:
            verbose: boolean value that decides whether or not debug messages
            are shown
        """
        self.name = name
        self.gamestate = GameState()
        self.verbose = verbose
        self.decider = importlib.import_module('..%s' % bot_type, package='bots/%s' % gen)

    def debug(self, msg):
        """
        Debug messages for the bot if `self.verbose` flag is set.

        Args:
            msg: string of the message to print
        """
        if self.verbose:
            print('%s: %s' % (self.name, msg))

    def read(self, msg):
        """
        Reads different messages from the server and parses information, then
        makes a decision.

        Args:
            msg: different messages sent by the Pokemon-Showdown server to the
            client
        """
        msg = msg.split('|')[1:]
        self.debug(msg)

        if len(msg) < 2 or msg[0] == '':
            pass
        elif msg[0] == 'request':
            self.gamestate.parse(msg[1], False)
            self.debug(json.dumps(self.gamestate.state, indent=4, sort_keys=True))
