"""
This module reads and stores GameState, then uses the Bot Class to then act on
that GameState.
"""

import json
import importlib

class GameState():
    """
    Stores gamestate as GameState.state, which is then used by the bot. This
    class also normalizes data to be used in ML purporses.
    """
    def __init__(self):
        self.state = {}

        # container for all pokemon data
        self.party = []
    def normalize(self, state):
        """
        Normalizes state data to be used.
        """
        pass

    def parse(self, state, normalize):
        """
        Takes in the state then processes it if ML, or copies it to state
        depending on needs.

        Args:
            state: state JSON string from Pokemon-Showdown
            normalize: whether or not to normalize data for ML
        """


        pokemon_party = json.loads(state)
        #  self.id = pokemon_party['']
        # take only the relevant stats for each pokemon, for now
        for ind, pokemon in enumerate(pokemon_party['side']['pokemon']):
            self.party.append({})
            self.party[ind]['id'] = pokemon['ident']
            self.party[ind]['moves'] = pokemon['moves']
            self.party[ind]['hp'] = pokemon['condition']
            self.party[ind]['item'] = pokemon['item']
            for name in pokemon['stats']:
                self.party[ind][name] = pokemon['stats'][name]

        # TODO: normalize the party values if chosen to
        if normalize:
            for poke in self.party:
                tr = list(map(lambda x: int(x), poke['hp'].split('/')))
                poke['hp'] = tr[0]/tr[1]
        

    def update(self, state,  normalize=True):
            """
            Updates the gamestate based on the information from STDOUT of the running
            showdown client, so that the bot can make a decision
            """
            
            data_type = state[0] 

            # upon switch, update the current active pokemon and its hp
            if data_type == 'switch':
                tmp = [x for x in self.party if x['id'].split(' ')[1] == state[1].split(' ')[1] and x['id'].split(' ')[0][:-1] in state[1].split(' ')[0][:-1]]
                print(state[1].split(' ')[0])
                if len(tmp) > 0:
                    self.state['active'] = tmp[0]
            elif data_type == 'turn':
                print('NOW: TURN {}'.format(state[1]))
            

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
