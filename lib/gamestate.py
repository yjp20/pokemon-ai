"""
This module contains the GameState, Player, Pokemon, and Move classes. These
classes help store the information within the board by parsing the showdown
protocol messages and changing the relevant variables.

Currently, this code is only fully applicable to gen1 and gen2 singles, since
the future generations and the doubles respectively require far more
complication in the code than is necessary.
"""

import copy
import json
import re
import logging

import lib.dex

LOGGER = logging.getLogger("pokemon-ai.gamestate")


class Move:
    """
    The Move class stores all the information related to a pokemon move and
    also can find moves based on their name and fill out the rest of the
    information.

    Args:
        gen (str): The string representing the gen of the game like ``gen1``.

    Attributes:
        gen (str): The string representing the gen of the game like ``gen1``.
        num (int): The move number as is shown in the official Pokedex.
        name (str): The standardized string name of the Pokemeon.
        category (str): One of ``Physical``, ``Special``, or ``Status``.
        target (str): One of ``normal`` or ``self``.
        type (str): The type of the move as a string. It is the capitalized full name of the type like ``Psychic``.
        pp (int): Current pp left of the move.
        pp_max (int): The maximum pp for the move.
        power (int): The power of the move.
        accuracy (float): The accuracy of the move as a float between 0~1.
        critratio (float): The crit ratio of the move, but as a multiplier of the normal chance.
        volatile_stauts (str):
            Indicates that this move may apply on of the volatile statuses like 'flinch' 
        status (str):
            Indicates that this move may apply one of the major non-volatile statuses like `psn`, `tox`, `brn`, and
            `par` that can be applied to the target pokemon.
        status_chance (str): The chance to apply the status of the move as a float between 0~1.
        drain (float): Percent drain of damage as a float between 0~1.
        recoil (float) Percent recoil of damage as a float between 0~1.
        heal (float): Percent heal of max hp as a float between 0~1.
        multihit:
            Raw representation of multihit as is done in the Pokemon Showdown Movedex. This can therefore either be a
            list or an int.
        multihit_multiplier: The average multiplier of the damage dealt by the multihit of power
        priority (int): Priority of the move which determines the order these moves execute while ignoring speed.
    """
    def __init__(self, gen: str):
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
        self.critratio = 1
        self.status = ""
        self.volatile_status = ""
        self.status_chance = ""
        self.drain = 0
        self.recoil = 0
        self.heal = 0

        # TODO

        self.multihit = 0
        self.multihit_multiplier = 0
        self.priority = 0

        # Move flags
        self.flags = {
            "authentic": False,
            "bite": False,
            "bullet": False,
            "charge": False,
            "contact": False,
            "dance": False,
            "defrost": False,
            "distance": False,
            "gravity": False,
            "heal": False,
            "mirror": False,
            "mystery": False,
            "nonsky": False,
            "powder": False,
            "protect": False,
            "pulse": False,
            "punch": False,
            "recharge": False,
            "reflectable": False,
            "snatch": False,
            "sound": False,
        }

    def find_move(self, guess=False):
        """
        Finds the move within the movedex using its name and fills in various
        stats and details about the move. The only thing that the guess
        paramter currently does is fill in the pp stat with the pp_max since
        that is the only "unknown" part of the move.
        """
        move = lib.dex.dexes[self.gen]["Movedex"][standardize_string(self.name)]
        self.category = move["category"]
        self.num = move["num"]
        self.power = move["basePower"]
        self.pp_max = move["pp"]
        self.target = move["target"]
        self.type = move["type"]

        if "critRatio" in move:
            critmults = []

            gen = int(self.gen[3])
            if gen <= 5:
                critmults = [0, 16, 8, 4, 3, 2]
            elif gen == 6:
                critmults = [0, 16, 8, 2, 1]
            elif gen > 6:
                critmults = [0, 24, 8, 2, 1]
            self.critratio = 1/critmults[move["critRatio"]]

        if "willCrit" in move:
            self.critratio = 1

        if "status" in move:
            self.status = move["status"]
            self.status_chance = 1

        if "recoil" in move:
            # Pokemon showdown provides recoil as a fraction
            self.recoil = move["recoil"][0] / move["recoil"][1]

        if "heal" in move:
            # Pokemon showdown provides heal as a fraction
            if int(self.gen[3]) >= 5:
                self.heal = move["heal"][0] / move["heal"][1]
            else:
                self.heal = 1/2

        if "drain" in move:
            # Pokemon showdown provides heal as a fraction
            self.drain = move["drain"][0] / move["drain"][1]

        if "multihit" in move:
            # Multihit is sometimes represented as a range, in which case it is written in a list.
            # It is otherwise written as a whole number, which then does not have probability concerns.
            # Thankfully, the only case where multihit is a range is between 2~5, where there is a
            # 1/3 probability for 2 or 3 hits and 1/6 probability for 4 or 5 hits. Therefore, this
            # code only contains an exception for that case
            if type(move["multihit"]) == list:
                self.multihit = [2, 5]
                self.multihit_multiplier = 4/6 + 6/6 + 4/6 + 5/6
            else:
                self.multihit = move["multihit"]
                self.multihit_multiplier = move["multihit"]

        if "secondary" in move:
            if move["secondary"] and "status" in move["secondary"]:
                if "status" in move["secondary"]:
                    self.status = move["secondary"]["status"]
                if "volatileStatus" in move["secondary"]:
                    self.volatile_status = move["secondary"]["volatileStatus"]

                self.status_chance = move["secondary"]["chance"] / 100

        if "secondaries" in move:
            # Since the first secondary is generally far more important, for now we will only store the first.
            if move["secondaries"][0] and "status" in move["secondaries"][0]:
                self.status = move["secondaries"][0]["status"]
                self.status_chance = move["secondaries"][0]["chance"] / 100

        if "flag" in move:
            for flag in move["flags"]:
                self.flags[flag] = True

        if isinstance(move["accuracy"], int):
            self.accuracy = move["accuracy"] / 100
        if isinstance(move["accuracy"], bool):
            self.accuracy = 1

        if guess:
            self.pp = move["pp"]


class Pokemon:
    """
    The Pokemon class stores all the information related to the pokemon and
    provides various functions that can help bots by accessing relevant
    information from the Pokedex from the Pokemon-Showdown project.
    """
    def __init__(self, gen, player_idx=None):
        self.gen = gen
        self.player_idx = player_idx
        self.num = 0
        self.name = ""
        self.faint = False
        self.level = 0
        self.maxhp = 100
        self.hp_percent = 1
        self.base_atk = 100
        self.base_def = 100
        self.base_spa = 100
        self.base_spd = 100
        self.base_spe = 100

        # mustrecharge is measured by the turn number where it was
        self.mustrecharge = -1
        self.ability = ""
        self.item = ""
        self.moves = dict()
        self.status = set()
        self.types = []
        self.transformed_as = None  # Is a Pokemon instance if the pokemon is transformed

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
            self.maxhp = (2 * pokemon["baseStats"]["hp"] + 30 + 63) * self.level / 100 + self.level + 10
            self.base_def = ((2 * pokemon["baseStats"]["def"] + 30 + 63) * self.level / 100 + 5)
            self.base_atk = ((2 * pokemon["baseStats"]["atk"] + 30 + 63) * self.level / 100 + 5)
            self.base_spa = ((2 * pokemon["baseStats"]["spa"] + 30 + 63) * self.level / 100 + 5)
            self.base_spd = ((2 * pokemon["baseStats"]["spd"] + 30 + 63) * self.level / 100 + 5)
            self.base_spe = ((2 * pokemon["baseStats"]["spe"] + 30 + 63) * self.level / 100 + 5)

    def is_mustrecharge(self, turn):
        return turn + 2 < self.mustrecharge

    @property
    def atk(self):
        multiplier = 1
        return self.base_atk

    @property
    def defense(self):
        return self.base_def

    @property
    def spa(self):
        return self.base_spa

    @property
    def spd(self):
        return self.base_spd

    @property
    def spe(self):
        return self.base_spe

    @property
    def hp(self):
        return self.hp_percent * self.maxhp

    @hp.setter
    def hp(self, hp):
        self.hp_percent = hp/self.maxhp

    def used_protect(self):
        return False  # TODO

    def is_poisoned(self):
        return "psn" in self.status

    def is_burned(self):
        return "brn" in self.status

    def is_leech_seeded(self):
        return False  # TODO


class Player:
    def __init__(self):
        self.active = ""
        self.boosts = dict()
        self.volatile_status = set()
        self.team = dict()
        self.secret = dict()
        self.is_player = False

        self.reset_boost()
        self.reset_status()

    def get_active(self, secret=False):
        if secret and self.active in self.team:
            return self.secret[self.active]
        if self.active in self.team:
            return self.team[self.active]
        return None

    def reset_boost(self):
        self.boosts = {
            "atk": 0,
            "def": 0,
            "spa": 0,
            "spd": 0,
            "spe": 0,
            "accuracy": 0,
        }

    def reset_status(self):
        self.status = set()


class GameState:
    """
    This class handles protocol messages sent as a Pokemon-Showdown battle
    stream and parses the data into a usable form.

    Attributes:
        gametype (str): Stores gametype like "singles" or "doubles"
        gen (str): Stores the generation as a string like "gen1"
        tier (str): TODO
        player_idx (int):
            Index of the player related to this gamestate. It is stored as the
            player number designated by showdown subtracted by 1.

            1. p1 -> 0

            2. p2 -> 1
        player_name (str):
            In-game name of the player or bot, used to match the player to this
            class's internal representation
        turn (int): Turn number of the game
        move_history: TODO
        players (list): TODO
    """
    def __init__(self, gen, name: str):
        self._sim_args_table = {}
        self._set_sim_table()

        # game meta data
        self.gametype = ""  # Stores gametype like "singles" or "doubles"
        self.gen = gen  # Stores the generation as a string like "gen1"
        self.tier = ""  # Kind of useless (?)
        self.player_idx = -1  # Index of gamestate owner
        self.player_name = name
        self._player_list = []  # [0] => p1's name | [1] => p2's name  etc...

        self.rated = False
        self.result = -1  # -1=undecided | 0=tie | x=winning player number
        self.inactive = False  # Inactive timer

        # for owner of this gamestate
        self.wait = False
        self.started = False
        self.force_switch = False

        # _player_map{name} => player idx related to that player's name
        # like "[Gen 1] Random Battle"
        self._player_map = {}

        self.players = []
        self.turn = 0
        self.upkeep = False

        self.move_history = []

        for i in range(0, 4):
            self.players.append(Player())

    def __dict__(self):
        data = {
            "gametype": self.gametype,
            "gen": self.gen,
            "tier": self.tier,
            "rated": self.rated,
            "result": self.result,
            "inactive": self.inactive,
            "started": self.started,
            "force_switch": self.force_switch,
            "players": self.players,
            "turn": self.turn,
            "upkeep": self.upkeep,
            "move_history": self.move_history,
            "player_idx": self.player_idx,
            "player_name": self.player_name,
        }
        return data

    def __str__(self):
        data = self.__dict__()

        def handle(x):
            if isinstance(x, set):
                return list(x)
            return x.__dict__

        return json.dumps(data,
                          default=handle,
                          skipkeys=True,
                          indent=4)

    def _reset_boost(self, player_idx: int):
        self.players[player_idx].reset_boost()

    def _reset_status(self, player_idx: int):
        self.players[player_idx].reset_status()

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
            '-prepare': self._noop,
            'cant': self._noop,
            '-boost': self._set_boost,
            '-mustrecharge': self._set_mustrecharge,
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
        if args[1] == self.player_name:
            self.player_idx = int(args[0][1]) - 1
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
            self.player_idx = int(data["side"]["id"][1]) - 1
            self.players[self.player_idx].secret = dict()
            pokemons = data["side"]["pokemon"]
            for pokemon in pokemons:
                new = Pokemon(self.gen, self.player_idx)
                (_, _, new.name) = read_ident(pokemon["ident"])
                (_, level) = read_details(pokemon["details"])
                (new.hp_percent, new.maxhp, new.faint, new.status) = read_condition(pokemon["condition"])
                new.level = int(level)
                new.base_def = int(pokemon["stats"]["def"])
                new.base_atk = int(pokemon["stats"]["atk"])
                new.base_spa = int(pokemon["stats"]["spa"])
                new.base_spd = int(pokemon["stats"]["spd"])
                new.base_spe = int(pokemon["stats"]["spe"])
                new.ability = pokemon["baseAbility"]
                new.item = pokemon["item"]
                for move_name in pokemon["moves"]:
                    move = Move(self.gen)
                    move.name = move_name
                    move.find_move()
                    new.moves[move_name] = move
                new.find_pokemon(False)
                self.players[self.player_idx].secret[standardize_string(new.name)] = new

    def _set_start(self, _):
        self.started = True

    def _set_upkeep(self, _):
        self.upkeep = True

    def _set_mustrecharge(self, args):
        (player, idx, name) = read_ident(args[0])
        player_idx = int(player) - 1
        self.players[player_idx].get_active().mustrecharge = self.turn
        if idx == self.player_idx:
            self.get_player_active().mustrecharge = self.turn

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
        (hp_percent, _, faint, status) = read_condition(args[2])
        player_idx = int(player) - 1
        name = standardize_string(name)

        if self.players[player_idx].get_active():
            self.players[player_idx].get_active().transformed_as = None

        self.players[player_idx].active = name
        self._reset_boost(player_idx)
        self._reset_status(player_idx)

        if name not in self.players[player_idx].team:
            new = Pokemon(self.gen, player_idx)
            new.name = name
            new.level = level
            new.hp_percent = hp_percent
            new.faint = faint
            new.status = status
            new.find_pokemon(True)
            self.players[player_idx].team[name] = new

    def _set_status(self, args):
        # Not sure if this and curestatus are strictly needed, but decided
        # to do it anyway for the sake of a more complete and ideally foolproof
        # system.
        player_idx = int(args[0][1]) - 1
        pokemon = self.players[player_idx].get_active()
        pokemon.status.add(args[1])

    def _set_cureteam(self, args):
        player_idx = int(args[0][1]) - 1
        for pokemon in self.players[player_idx]:
            pokemon.status = set()

    def _set_curestatus(self, args):
        player_idx = int(args[0][1]) - 1
        pokemon = self.players[player_idx].get_active()
        pokemon.status.remove(args[1])

    def _set_clearboost(self, args):
        player_idx = int(args[0][1]) - 1
        self._reset_boost(player_idx)

    def _set_clearallboost(self, _):
        for i in range(0, 4):
            self._reset_boost(i)

    def _set_damage(self, args):
        player_idx = int(args[0][1]) - 1
        (hp_percent, _, faint, status) = read_condition(args[1])
        pokemon = self.players[player_idx].get_active()
        pokemon.hp_percent = hp_percent
        pokemon.faint = faint
        pokemon.status = status

    def _set_boost(self, args):
        player_idx = int(args[0][1]) - 1
        self.players[player_idx].boosts[args[1]] += int(args[2])

    def _set_unboost(self, args):
        player_idx = int(args[0][1]) - 1
        self.players[player_idx].boosts[args[1]] -= int(args[2])

    def _set_transform(self, args):
        player_idx = int(args[0][1]) - 1
        other_idx = int(args[1][1]) - 1
        player_pokemon = self.players[player_idx].get_active()
        other_pokemon = self.get_active(other_idx)
        player_pokemon.transformed_as = copy.deepcopy(other_pokemon)
        if player_idx == self.player_idx:
            self.get_player_active().transformed_as = copy.deepcopy(other_pokemon)

    def _set_hp(self, args):
        player_idx = int(args[0][1]) - 1
        pokemon = self.players[player_idx].get_active()
        hp_percent, _, _, _ = read_condition(args[1])
        pokemon.hp_percent = hp_percent

    def _set_move(self, args):
        player_idx = int(args[0][1]) - 1
        move_name = standardize_string(args[1])
        if move_name == 'recharge':
            return
        pokemon = self.players[player_idx].get_active()
        if move_name not in pokemon.moves:
            move = Move(self.gen)
            move.name = move_name
            move.find_move(True)
            pokemon.moves[move_name] = move
        pokemon.moves[move_name].pp -= 1

    def _set_volatile_status_start(self, args):
        player_idx = int(args[0][1]) - 1
        self.players[player_idx].status.add(standardize_string(args[1]))

    def _set_volatile_status_end(self, args):
        player_idx = int(args[0][1]) - 1
        std_string = standardize_string(args[1])
        if std_string in self.players[player_idx].status:
            self.players[player_idx].status.remove(standardize_string(args[1]))

    def get_boost(self, idx, name) -> int:
        return self.players[idx].boosts[name]

    def parse(self, line):
        """
        Accepts line from simulator and takes appropiate action in modifying
        the gamestate. An example message from the simulator will look
        something like `|{action}|{argument 1}|{argument 2 ...}`, so this
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


def _error(args):
    LOGGER.error(args)


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
