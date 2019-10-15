"""

"""

# pylint: disable=too-many-instance-attributes

import json

class GameState():
    """
    Stores gamestate as GameState.state, which is then used by the bot. This
    class also normalizes data to be used in ML purporses.
    """
    def __init__(self):
        self._set_sim_table()

        self.meta = {}
        self.meta.gametype = None
        self.meta.gen = None
        self.meta.tier = None
        self.meta.rated = False
        self.meta.result = -1
        self.meta.inactive = None

        self.started = False
        self.party = [] # Stores "complete" information about the bot's pokemons
        self.players = [] # Stores "incomplete" information about all pokemons
        self.turn = 0
        self.upkeep = False

    def _noop(self, _):
        pass

    def _set_sim_table(self):
        # master table for all callables
        self._sim_args_table = {
            'clearpoke':    self._noop,
            'teamsize':     self._noop,
            'teampreview':  self._noop,
            'gametype':     self._set_gametype,
            'gen':          self._set_gen,
            'inactive':     self._set_inactive_on,
            'inactiveoff':  self._set_inactive_off,
            'player':       self._set_player,
            'poke':         self._set_team_preview,
            'rated':        self._set_rated_bool,
            'request':      self._set_request,
            'rule':         self._set_rule,
            'start':        self._set_start,
            'tie':          self._set_tie,
            'tier':         self._set_tier,
            'turn':         self._set_turn,
            'upkeep':       self._set_upkeep,
            'win':          self._set_win,
        }

    def _set_gametype(self, args):
        self.meta.gametype = args[0]

    def _set_gen(self, args):
        self.meta.gen = args[0]

    def _set_inactive_on(self, _):
        self.meta.inactive = True

    def _set_inactive_off(self, _):
        self.meta.inactive = False

    def _set_player(self, args):
        pass

    def _set_team_preview(self, args):
        pass

    def _set_rated_bool(self, args):
        if args:
            self.meta.rated = False
        else:
            self.meta.rated = True

    def _set_tier(self, args):
        self.meta.tier = args[0]

    def _set_request(self, args):
        data = json.load(args[0])
        print(data) # TODO

    def _set_rule(self, args):
        pass

    def _set_start(self, _):
        self.meta.started = True

    def _set_upkeep(self, _):
        self.upkeep = True

    def _set_turn(self, args):
        self.turn = args[0]
        self.upkeep = False

    def _set_win(self, args):
        self.meta.result = args[0]

    def _set_tie(self, _):
        self.meta.result = 0

    def parse(self, line):
        """Accepts line from simulator and takes appropiate action in modifying the gamestate.

        Args:
            line (str): line that the simulator sends to the bot, which is then passed here
        """
        if not line:
            return
        line = line[1:]
        args = line.split('|')
        func = args[0]
        if not func:
            return
        self._sim_args_table[func](args[1:])
