import json


class GameState():
    """
    Stores gamestate as GameState.state, which is then used by the bot. This
    class also normalizes data to be used in ML purporses.
    """
    def __init__(self):
        self.state = {}

        # container for all pokemon data
        self.party = []

        self._set_sim_table()
    def noop(self, x, *j):
        pass

    def _set_sim_table(self):
        # master table for all callables
        self._sim_args_table = {
            'player': self.set_player,
            'teamsize': self.set_teamsize,
            'gametype': self.set_gametype,
            'gen': self.set_gen_num,
            'tier': self.set_tier,
            'rated': self.set_rated_bool,
            'rule': self.add_rule,
            'clearpoke': self.team_preview_bool,
            'poke': self.set_team_preview,
            'start': self.set_start,
            'request': self.update_request_status,
            'inactive': self.set_inactive,
            'inactiveoff': self.set_inactive_bool,
            'upkeep': self.upkeep,
            'turn': self.update_turn_number,
            'win': self.update_win_status,
            'tie': self.update_tie
        }
    def set_player(self, args):
        if not self.state['players']:
            self.state['players'] = {}
        self.state['players'][args[0]] = {'username': args[1], 'elo': int(args[3]) if len(args)>3 else 0, 'party': []}
    
    def set_teamsize(self, args):
        self.state['players'][args[0]]['teamsize'] = int(args[1])
    
    def set_gametype(self, args):
        self.gametype = args[0]
    
    def set_gen_num(self, args):
        self.gen_n = args[0]
    
    def set_tier(self, args):
        self.tier = args[0]
    
    def set_rated_bool(self, args):
        if args:
            self.rated = 1
        else:
            self.rated = 2
    
    def add_rule(self, args):
        if not self.state['ruleset']:
            self.state['ruleset'] = []
        self.state['ruleset'].append(args[0])
    
    def team_preview_bool(self, args):
        self.state['bool'] = True
    
    def set_team_preview(self, args):
        self.state[args[0]]['party'].append([args[1], args[2]]) 

    def set_start(self, args):
        self.started = True
        self.state['info'] = json.loads(args[0])
    
    def set_inactive(self, args):
        self.inactive = True
        self.inactive_poke = True
    
    def set_inactive_bool(self, args):
        self.inactive = False
    
    def upkeep(self, args):
        self.upk = True

    def update_turn_number(self, args):
        self.turns = args[0]
        self.upk = False

    def update_win_status(self, args):
        self.winner = args[0]
    
    def update_tie(self, args):
        self.winner = 'TIE'
    #TODO add request JSON to updating functionality
    def request(self, args):
        self.move_requested = True
        self.state
    def normalize(self, state):
        """
        Normalizes state data to be used.
        """
        pass

    def sim_read(sim_string):
        sim_string = sim_string[1:]
        full_arguments = sim_string.split('|')
        fn = full_arguments[0]
        if not fn:
            return
        args = full_arguments[1:]

        self._sim_args_table[fn](args)
        return
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
            

