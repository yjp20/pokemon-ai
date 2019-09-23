import json

class GameState():
    """
    Stores gamestate as GameState.state, which is then used by the bot. This
    class also normalizes data to be used in ML purporses.
    """
    def __init__(self):
        self.party = []
        self.active = None

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
        # self.id = pokemon_party['']
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


    def update(self, state, normalize=True):
        """
        Updates the gamestate based on the information from STDOUT of the running
        showdown client, so that the bot can make a decision
        """

        data_type = state[0]
