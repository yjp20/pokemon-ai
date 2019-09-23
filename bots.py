"""
The Bot class dynamically loads individual bot files.
"""

import importlib
import gamestate

class Bot():
    """
    Bot that tkes in state message from Pokemon-Showdown and makes decisions
    based on that state information.
    """
    def __init__(self, gen, bot_type):
        """
        Args:
            gen (str): generation of the simulator such as 'gen1'
            bot_type (str): the bot type as defined in ai/{gen}/{bot_type}
        """
        self.gamestate = gamestate.GameState()
        bot_module = importlib.import_module('.%s' % bot_type, package='ai.%s' % gen)
        self._choose = bot_module.choose_move

    def read(self, line):
        """ Reads different messages from the server and parses information.

        Args:
            line (str): different messages sent by the Pokemon-Showdown server to the client

        Return:
            str: Empty if no move is made
        """
        msg = line.split('|')[1:]
        action = msg[1]

        if len(msg) < 2 or action == '':
            pass
        elif action == 'request':
            self.gamestate.parse(msg[1], False)
        elif action == '':
            pass

    def choose(self):
        """  Wrapper for the internal _choose function """
        choice = self._choose(self.gamestate)
        if 'modifier' in choice:
            return f'{choice["type"]} {choice["id"]} {choice["modifier"]}'
        return f'{choice["type"]} {choice["id"]}'
