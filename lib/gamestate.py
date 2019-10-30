"""
Module contains GameState class that adjusts data based on the input from the
simulator, either local, online, or even replays.

Currently, this module only supports singles gamemodes, but it should be not
_too_ difficult to add support to doubles. However, some of the core logic will
have to be rethought.

There are also some minor actions from the newer generations that are not
currently handled. Those should be relatively easy to implement.
"""

# pylint: disable=too-many-instance-attributes, invalid-name

import copy
import json
import re
import logging

import lib.dex

LOGGER = logging.getLogger("pokemon-ai.local")


class Move:
    """
    The Move class stores all the information related to a pokemon move.
    """
    def __init__(self, gen):
        # Move meta data
        self.gen = gen
        self.num = 0
        self.name = ""

        # Move attributes
        self.category = ""  # Physical, Special, Status
        self.target = ""  # normal, self
        self.type = ""
        self.pp = 0
        self.pp_max = 0
        self.power = 100
        self.accuracy = 1

        # Move flags
        self.authentic = False
        self.bite = False
        self.bullet = False
        self.charge = False
        self.contact = False
        self.dance = False
        self.defrost = False
        self.distance = False
        self.gravity = False
        self.heal = False
        self.mirror = False
        self.mystery = False
        self.nonsky = False
        self.powder = False
        self.protect = False
        self.pulse = False
        self.punch = False
        self.recharge = False
        self.reflectable = False
        self.snatch = False
        self.sound = False

    def find_move(self, guess=False):
        """
        Finds the move within the movedex using its name and fills in various
        stats and details about the move. The only thing that the guess
        paramter currently does is fill in the pp stat with the pp_max.
        """
        move = lib.dex.dexes[self.gen]["Movedex"][standardize_string(self.name)]
        # print(json.dumps(move, indent=4))
        self.category = move["category"]
        self.num = move["num"]
        self.power = move["basePower"]
        self.pp_max = move["pp"]
        self.target = move["target"]
        self.type = move["type"]

        if guess:
            self.pp = move["pp"]

        if isinstance(move["accuracy"], int):
            self.accuracy = move["accuracy"] / 100
        if isinstance(move["accuracy"], bool):
            self.accuracy = 1
        if "flag" in move:
            for flag in move["flags"]:
                self.__setattr__(flag, True)


class Pokemon:
    """
    The Pokemon class stores all the information related to the pokemon and
    provides various functions that can help bots by accessing relevant
    information from the Pokedex from the Pokemon-Showdown project.
    """
    def __init__(self, gen):
        self.gen = gen
        self.num = 0
        self.name = ""
        self.level = 0
        self.hp = 1
        self.maxhp = 100
        self.faint = False
        self.atk = 100
        self.defense = 100
        self.spa = 100
        self.spd = 100
        self.spe = 100
        self.ability = ""
        self.item = ""
        self.moves = dict()
        self.status = set()
        self.types = []
        self.transformed_as = None # Is a Pokemon instance if the pokemon is transformed

    def find_pokemon(self, guess=False):
        """
        Finds a pokemon within the pokedex using its name and fills in various
        pokemon stats with the found information. If the `guess` parameter is
        false, only the pokemon number, name, and type are filled in, but with
        `guess` true, hp, def, atk, spa, spd, and spe are filled in.

        Args:
            guess (bool): whether to guess the aforementioned pokemon stats.
        """
        pokemon = lib.dex.dexes[self.gen]["Pokedex"][standardize_string(self.name)]
        self.num = pokemon["num"]
        self.types = pokemon["types"]
        if guess:
            # Assumes max EVs and max IVs
            # Presumably, it should make the bot play more safe
            self.maxhp = (2 * pokemon["baseStats"]["hp"] + 30 + 63 +
                          100) * self.level / 100 + 10
            self.defense = ((2 * pokemon["baseStats"]["def"] + 30 + 63 + 100) *
                            self.level / 100 + 5)
            self.atk = ((2 * pokemon["baseStats"]["atk"] + 30 + 63 + 100) *
                        self.level / 100 + 5)
            self.spa = ((2 * pokemon["baseStats"]["spa"] + 30 + 63 + 100) *
                        self.level / 100 + 5)
            self.spd = ((2 * pokemon["baseStats"]["spd"] + 30 + 63 + 100) *
                        self.level / 100 + 5)
            self.spe = ((2 * pokemon["baseStats"]["spe"] + 30 + 63 + 100) *
                        self.level / 100 + 5)


def _error(args):
    LOGGER.error(args)


class GameState:
    """
    Stores gamestate as GameState.state, which is then used by the bot. This
    class also normalizes data to be used in ML purporses.
    """
    def __init__(self, gen):
        self._sim_args_table = {}
        self._set_sim_table()

        # META DATA
        self.gametype = ""  # Stores gametype like "singles" or "doubles"
        self.gen = gen  # Stores the generation as a string like "gen1"
        self.tier = ""  # Kind of useless (?)
        self._player_list = []  # [0] => p1's name | [1] => p2's name  etc...

        # _player_map{name} => player idx related to that player's name
        # like "[Gen 1] Random Battle"
        self._player_map = {}

        self.rated = False
        self.result = -1  # -1=undecided | 0=tie | x=winning player number
        self.inactive = False  # Inactive timer

        # USEFUL DATA
        self.wait = False
        self.started = False
        self.force_switch = False

        # Stores "perfect" information about the bot's pokemons by
        # containing the bot's pokemons in an array
        self.party = []

        # Stores "imperfect" information about all pokemons by
        # containing an array for each player with each array looking
        # something like [Pokemon(), Pokemon(), ...]
        self.players = []
        self._player_pokemon_map = dict()

        self.player_active = [""] * 4
        self.player_boost = [dict()] * 4
        self.player_status = [set()] * 4
        self.turn = 0
        self.upkeep = False
        self.moves = []

        for i in range(0, 4):
            self._reset_boost(i)
            self._reset_status(i)
            self.players.append(dict())

    def __str__(self):
        data = {
            "gametype": self.gametype,
            "gen": self.gen,
            "tier": self.tier,
            "rated": self.rated,
            "result": self.result,
            "inactive": self.inactive,
            "started": self.started,
            "force_switch": self.force_switch,
            "party": self.party,
            "players": self.players,
            "player_boost": self.player_boost,
            "player_active": self.player_active,
            "turn": self.turn,
            "upkeep": self.upkeep,
            "moves": self.moves,
        }

        def handle(x):
            if isinstance(x, set):
                return list(x)
            return x.__dict__

        return json.dumps(data,
                          default=handle,
                          skipkeys=True,
                          indent=4)

    def _reset_boost(self, player_idx: int):
        self.player_boost[player_idx] = {
            "atk": 0,
            "def": 0,
            "spa": 0,
            "spd": 0,
            "spe": 0,
            "accuracy": 0,
        }

    def _reset_status(self, player_idx: int):
        self.player_status[player_idx] = set()

    def _set_sim_table(self):
        self._sim_args_table = {
            'error': _error,
            'clearpoke': self._noop,
            'teamsize': self._noop,
            'teampreview': self._noop,
            'rule': self._noop,
            'gen': self._noop,
            '-hint': self._noop,
            'gametype': self._set_gametype,
            'inactive': self._set_inactive_on,
            'inactiveoff': self._set_inactive_off,
            'player': self._set_player,
            'poke': self._set_team_preview,
            'rated': self._set_rated_bool,
            'request': self._set_request,
            'start': self._set_start,
            'tie': self._set_tie,
            'tier': self._set_tier,
            'turn': self._set_turn,
            'upkeep': self._set_upkeep,
            'win': self._set_win,

            # Imperfect
            '-crit': self._noop,
            '-fail': self._noop,
            '-immune': self._noop,
            '-hitcount': self._noop,
            '-miss': self._noop,
            '-notarget': self._noop,
            '-resisted': self._noop,
            '-supereffective': self._noop,
            '-mustrecharge': self._noop,
            '-prepare': self._noop,
            'cant': self._noop,
            '-boost': self._set_boost,
            '-cureteam': self._set_cureteam,
            '-curestatus': self._set_curestatus,
            '-damage': self._set_damage,
            '-heal': self._set_damage,
            '-sethp': self._set_hp,
            '-start': self._set_volatile_status_start,
            '-activate': self._set_volatile_status_start,
            '-end': self._set_volatile_status_end,
            '-status': self._set_status,
            '-transform': self._set_transform,
            '-unboost': self._set_unboost,
            '-clearboost': self._set_clearboost,
            '-clearallboost': self._set_clearallboost,
            'faint': self._noimpl,
            'move': self._set_move,
            'switch': self._set_switch,
        }

    def _noop(self, _):
        pass

    def _noimpl(self, _):
        pass

    def _set_gametype(self, args):
        self.gametype = args[0]

    def _set_inactive_on(self, _):
        self.inactive = True

    def _set_inactive_off(self, _):
        self.inactive = False

    def _set_player(self, args):
        self._player_map[args[1]] = int(args[0][1])
        self._player_list.append(args[1])

    def _set_team_preview(self, args):
        pass

    def _set_rated_bool(self, args):
        if args:
            self.rated = False
        else:
            self.rated = True

    def _set_tier(self, args):
        self.tier = args[0].strip()

    def _set_request(self, args):
        data = json.loads(args[0])
        self.force_switch = False
        self.wait = False
        if "wait" in data:
            self.wait = True
        if "forceSwitch" in data:
            self.force_switch = True
        if "side" in data:
            self.party = []
            pokemons = data["side"]["pokemon"]
            for pokemon in pokemons:
                new = Pokemon(self.gen)
                (_, _, new.name) = read_ident(pokemon["ident"])
                (_, level) = read_details(pokemon["details"])
                (new.hp, new.maxhp, new.faint,
                 new.status) = read_condition(pokemon["condition"])
                new.level = int(level)
                new.defense = int(pokemon["stats"]["def"])
                new.atk = int(pokemon["stats"]["atk"])
                new.spa = int(pokemon["stats"]["spa"])
                new.spd = int(pokemon["stats"]["spd"])
                new.spe = int(pokemon["stats"]["spe"])
                new.ability = pokemon["baseAbility"]
                new.item = pokemon["item"]
                for move_name in pokemon["moves"]:
                    move = Move(self.gen)
                    move.name = move_name
                    move.find_move()
                    new.moves["move_name"] = move
                new.find_pokemon(False)
                self.party.append(new)

    def _set_start(self, _):
        self.started = True

    def _set_upkeep(self, _):
        self.upkeep = True

    def _set_turn(self, args):
        self.turn = int(args[0])
        self.upkeep = False

    def _set_win(self, args):
        self.result = self._player_map[args[0].strip()]

    def _set_tie(self, _):
        self.result = 0

    def _set_switch(self, args):
        (player, _, _) = read_ident(args[0])
        (name, level) = read_details(args[1])
        (hp, _, faint, status) = read_condition(args[2])
        player_idx = int(player) - 1
        name = standardize_string(name)

        if self.player_active[player_idx]:
            self.get_active(player_idx).transformed_as = None

        self.player_active[player_idx] = name
        self._reset_boost(player_idx)
        self._reset_status(player_idx)

        if name not in self.players[player_idx]:
            new = Pokemon(self.gen)
            new.name = name
            new.level = level
            new.hp = hp
            new.faint = faint
            new.status = status
            new.find_pokemon(True)
            self.players[player_idx][name] = new

    def _set_status(self, args):
        # Not sure if this and curestatus are strictly needed, but decided
        # to do it anyway for the sake of a more complete and ideally foolproof
        # system.
        player_idx = int(args[0][1]) - 1
        pokemon = self.get_active(player_idx)
        pokemon.status.add(args[1])

    def _set_cureteam(self, args):
        player_idx = int(args[0][1]) - 1
        for pokemon in self.players[player_idx]:
            pokemon.status = set()

    def _set_curestatus(self, args):
        player_idx = int(args[0][1]) - 1
        pokemon = self.get_active(player_idx)
        pokemon.status.remove(args[1])

    def _set_clearboost(self, args):
        player_idx = int(args[0][1]) - 1
        self._reset_boost(player_idx)

    def _set_clearallboost(self, _):
        for i in range(0, 4):
            self._reset_boost(i)

    def _set_damage(self, args):
        player_idx = int(args[0][1]) - 1
        (hp, _, faint, status) = read_condition(args[1])
        pokemon = self.get_active(player_idx)
        pokemon.hp = hp
        pokemon.faint = faint
        pokemon.status = status

    def _set_boost(self, args):
        player_idx = int(args[0][1]) - 1
        self.player_boost[player_idx][args[1]] += int(args[2])

    def _set_unboost(self, args):
        player_idx = int(args[0][1]) - 1
        self.player_boost[player_idx][args[1]] -= int(args[2])

    def _set_transform(self, args):
        player_idx = int(args[0][1]) - 1
        other_idx = int(args[1][1]) - 1
        player_pokemon = self.get_active(player_idx)
        other_pokemon = self.get_active(other_idx)
        player_pokemon.transformed_as = copy.deepcopy(other_pokemon)

    def _set_hp(self, args):
        player_idx = int(args[0][1]) - 1
        pokemon = self.get_active(player_idx)
        hp, _, _, _ = read_condition(args[1])
        pokemon.hp = hp

    def _set_move(self, args):
        player_idx = int(args[0][1]) - 1
        move_name = standardize_string(args[1])
        if move_name == 'recharge':
            return
        pokemon = self.get_active(player_idx)
        if move_name not in pokemon.moves:
            move = Move(self.gen)
            move.name = move_name
            move.find_move(True)
            pokemon.moves[move_name] = move
        pokemon.moves[move_name].pp -= 1

    def _set_volatile_status_start(self, args):
        player_idx = int(args[0][1]) - 1
        self.player_status[player_idx].add(standardize_string(args[1]))

    def _set_volatile_status_end(self, args):
        player_idx = int(args[0][1]) - 1
        std_string = standardize_string(args[1])
        if std_string in self.player_status[player_idx]:
            self.player_status[player_idx].remove(standardize_string(args[1]))

    def get_active(self, player_idx: int) -> Pokemon:
        return self.players[player_idx][self.player_active[player_idx]]

    def parse(self, line):
        """
        Accepts line from simulator and takes appropiate action in modifying
        the gamestate. An example message from the simulator will look
        something like "|{action}|{argument 1}|{argument 2 ...}", so this
        function will look for the corresponding action as defined within the
        _sim_args_table.

        Args:
            line (str):
                line that the simulator sends to the bot, which is
                then passed here
        """
        if not line:
            return
        line = line.strip()
        line = line[1:]
        args = line.split('|')
        action = args[0]
        if not action:
            return
        if action in self._sim_args_table:
            self._sim_args_table[action](args[1:])
        else:
            LOGGER.error("Not Handled: %s" % action)


def standardize_string(string: str) -> str:
    """
    Standardizes a given input string such as the name of a pokemon or the
    name of a move. The standardization consists of striping all
    non-alphanumeric characters and making the string all lower case.

    Args:
        string (str): input name of a pokemon / move

    Returns:
        str: the standardized and sanitized string
    """
    return re.sub(r"[^a-zA-Z0-9]", "", string).lower()


def read_ident(ident_string: str) -> (int, str, str):
    """
    Reads a string like "p1a: Magikarp" and returns the relevant data encoded
    within that string.
    """
    [player, idx, name] = re.search(r"p(\d)(\w*): (.*)", ident_string).groups()
    return int(player), idx, name


def read_details(detail_string: str) -> (str, int):
    """
    Reads a string like "Magikary, L89" and returns the relevant data encoded
    within that string.
    """
    [name, level] = re.search(r"([^,]+), L(\d+)", detail_string).groups()
    return name, int(level)


def read_condition(condition_string: str) -> (float, float, bool, set):
    """
    Reads a string like "100/200 slp" and returns the relevant data encoded
    within that string.
    """
    faint = False
    hp = 0
    maxhp = 100
    status = []
    if re.match(r"\d+ fnt", condition_string):
        hp = 0
        faint = True
    if re.match(r"(\d+)/(\d+)( \w+)*", condition_string):
        res = re.search(r"(\d+)/(\d+)( \w+)*", condition_string).groups()
        hp = int(res[0]) / int(res[1])
        maxhp = int(res[1])
        faint = False
        for status_condition in res[2:]:
            if status_condition is not None:
                status.append(status_condition.strip())
    return hp, maxhp, faint, set(status)
