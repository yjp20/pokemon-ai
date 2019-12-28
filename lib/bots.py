"""
This module holds the Bot class, which can dynamically load files that provide
the `choose_move` function and use it as the decider for the Bot agent. The Bot
also handles managing the GameState limited to its current knowledge of the board.
"""

import importlib
import lib.gamestate


class Bot():
    """
    The Bot class takes in messages in the form of Pokemon-Showdown protocol
    messages and makes decisions based on that state information based on the
    `name` and `gen` of the bot which are used to find the bot file to load to
    be used as the logic for the bot.
    """
    def __init__(self, name, gen, bot_type):
        """
        Args:
            gen (str): generation of the simulator such as 'gen1'
            bot_type (str): the bot type as defined in ai/{gen}/{bot_type}
        """
        self.name = name
        self.gamestate = None
        self.gen = gen
        self.new_gamestate()
        bot_module = importlib.import_module('.%s' % bot_type, package='ai.%s' % gen)
        self._choose = bot_module.choose_move

    def read(self, line):
        """ Reads different messages from the server and parses information.

        Args:
            line (str): different messages sent by the Pokemon-Showdown server
                        to the client
        """
        self.gamestate.parse(line)

    def choose(self):
        """  Wrapper for the internal _choose function and formats the `choice`
        dict returned by it to a message usable in Pokemon-Showdown.

        Returns:
            str: a string declaring the move chosen by the bot in the format wanted by the Pokemon-Shodwon protocol
        """
        choice = self._choose(self.gamestate)
        if 'modifier' in choice:
            return f'{choice["type"]} {choice["id"]} {choice["modifier"]}'
        return f'{choice["type"]} {choice["id"]}'

    def new_gamestate(self):
        """ Creates a new GameState with relevant parameters that makes it
        specific to this agent. """
        self.gamestate = lib.gamestate.GameState(self.gen, self.name)
