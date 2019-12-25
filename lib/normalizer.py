"""
Module to normalize the gamestate to be used in various ML bot implementations.
The output of the normalize function results in the desired features ranging
from 0 to 1 as is the standard for pytorch.

The normalized array has the following structure:

index => value

0 => is ally active faster than opp active
1 => percent of my unknown pokemon [0, 1]
2 => percent of opp unknown pokemon [0, 1]

for each pokemon of active [ally, opponent]:
    0 => percentage of unknown moves [0, 1]
    1 => level [60, 100]
    2 => health percentage [0, 1]
    3 => bug type
    4 => dragon type
    5 => electric type
    6 => fighting type
    7 => fire type
    8 => flying type
    9 => ghost type
    10 => grass type
    11 => ground type
    12 => ice type
    13 => normal type
    14 => poison type
    15 => psychic type
    16 => rock type
    17 => water type
    18 => is poisoned
    19 => is toxiced
    20 => is burned
    21 => is paralyzed
    22 => is confused
    23 => is frozen
    24 => is sleeping
    25 => base attack [0, 350] (logistic curve)
    26 => base defense [0, 350] (logistic curve)
    27 => base special [0, 350] (logistic curve)
    28 => base speed [0, 350] (logistic curve)
    29 => real attack [0, 1300] (logistic curve) (only for attack, divide by 2 if burned) (multiply based on modifiers)
    30 => real defense [0, 1300] (logistic curve) (*2 if reflect)
    31 => real special [0, 1300] (logistic curve)
    32 => real speed [0, 1300] (logistic curve) (only for speed, divide by 4 if paralyzed)
    33 => attack modifier [-6, 6]
    34 => defense modifier [-6, 6]
    35 => special modifier [-6, 6]
    36 => speed modifier [-6, 6]
    37 => used_protect (whether or not they used protect last turn)
    38 => is_leech_seeded
    39 => is underground (using dig)
    40 => is in the sky (using fly)
    41 => is recovering (after using hyper beam or something)
    42 => is charging (using sky attack or something)

    for each move of pokemon (4 times):
            0 => move1 power (if multi-hit, pls do weighted average based on probabilities) [0, 200] (*2 manually if earthquake and opp is digging) (logistic regression !!!!!)
            1 => move1 pp remaining [0, 1]
            2 => move1 acc of current pokemon [0, 1]
            3 => move1 crit chance [0, 1]
            3.5 => move1 predicted % health damage [0, 1] (use RANDOM = 0.9)
            4 => move1 will it kill the enemy pokemon? (for damage calc, assume RANDOM = 0.9)
            5 => move1 bug type
            6 => move1 dragon type
            7 => move1 electric type
            8 => move1 fighting type
            9 => move1 fire type
            10 => move1 flying type
            11 => move1 ghost type
            12 => move1 grass type
            13 => move1 ground type
            14 => move1 ice type
            15 => move1 normal type
            16 => move1 poison type
            17 => move1 psychic type
            18 => move1 rock type
            19 => move1 water type
            20 => move1 is_physical_attack (1 if physical move, -1 if not)
            21 => move1 is_special_attack (1 if special move, -1 if not)
            22 => move1 modify_ally_atk (number of stages change * 0.5)
            23 => move1 modify_ally_def
            24 => move1 modify_ally_spc
            25 => move1 modify_ally_spd
            26 => move1 modify_opp_atk
            27 => move1 modify_opp_def
            28 => move1 modify_opp_spc
            29 => move1 modify_opp_spd
            30 => move1 flinch_opp
            31 => move1 freeze_opp
            32 => move1 burn_opp
            33 => move1 paralyze_opp
            34 => move1 confuse_opp
            35 => move1 poison_opp
            36 => move1 toxic_opp
            37 => move1 sleep_opp
            38 => move1 is_counter (no mirror coat, only counter in gen 1)
            39 => move1 traps_opp (moves like bind or clamp or whirlpool traps opponent on field)
            40 => move1 drains_health (only true for mega drain, giga drain, since all such moves drain 50% of dmg dealt in gen 1)
            41 => move1 has_recoil (all such moves have 25% recoil on dmg dealt, so just 1 or -1)
            42 => move1 must_recharge (hyper beam, giga impact, etc)
            43 => move1 OHKO (one hit KO!)
            44 => move1 is_explosion (also implies 250 dmg)
            45 => move1 takes_two_turns (moves like dig, fly)
            46 => move1 recoil_if_miss (high jump kick, jump kick. Both have ½ recoil)
            47 => move1 recovers_health (1 if recover or soft-boiled, -1 if not) (the only other health recovering move, rest, is otherwise taken care of)
            48 => move1 is_reflect
            49 => move1 copies_opp_move
            50 => move1 damages_based_on_level (night shade, seismic toss)
            51 => move1 is_rest
            52 => move1 is_transform


for each nonactive pokemon of [ally, opponent]:
    0 => is fainted
    1 => level [60, 100]
    2 => health percentage [0, 1]
    3 => bug type
    4 => dragon type
    5 => electric type
    6 => fighting type
    7 => fire type
    8 => flying type
    9 => ghost type
    10 => grass type
    11 => ground type
    12 => ice type
    13 => normal type
    14 => poison type
    15 => psychic type
    16 => rock type
    17 => water type
    18 => is poisoned
    19 => is toxiced
    20 => is burned
    21 => is paralyzed
    22 => is frozen
    23 => is sleeping
    24 => base attack [0, 350] (logistic curve)
    25 => base defense [0, 350] (logistic curve)
    26 => base special [0, 350] (logistic curve)
    27 => base speed [0, 350] (logistic curve)
    28 => percent of unknown moves [0, 1]


"""

TYPES = ('Bug', 'Dragon', 'Electric', 'Fighting', 'Fire', 'Flying', 'Ghost', 'Grass', 'Ground', 'Ice', 'Normal', 'Poison', 'Psychic', 'Rock', 'Water')
STATUS = {'brn', 'frz', 'par', 'psn', 'tox', 'slp'}
MIN_LEVEL = 60


def damage_calc(gamestate):
    pass

def normalize(g, player_idx):
    pi = player_idx
    oi = pi^1
    n = dict()
    n['player_faster_than_opp'] = g.get_active(pi).spd >= g.get_active(oi).spd

    for i in (('player', pi, oi), ('opponent', oi, pi)):
        name, idx, opp = i
        n[f'percent_known_of_{name}'] = len(g.players[idx-1]) / 6
        n[f'percent_known_moves_of_{name}_active'] = len(g.get_active(idx).moves) / 4
        n[f'level_of_{name}_active'] = (g.get_active(idx).level-MIN_LEVEL) / (100-MIN_LEVEL)

        n[f'base_atk_{name}_active'] = g.get_active(idx).atk / 350
        n[f'base_def_{name}_active'] = g.get_active(idx).defense / 350
        n[f'base_spa_{name}_active'] = g.get_active(idx).spa / 350
        n[f'base_spd_{name}_active'] = g.get_active(idx).spd / 350
        n[f'base_spe_{name}_active'] = g.get_active(idx).spe / 350

        n[f'real_atk_{name}_active'] = g.get_boost(idx, 'atk') * g.get_active(idx).atk / 1500
        n[f'real_def_{name}_active'] = g.get_boost(idx, 'def') * g.get_active(idx).defense / 1500
        n[f'real_spa_{name}_active'] = g.get_boost(idx, 'spa') * g.get_active(idx).spa / 1500
        n[f'real_spd_{name}_active'] = g.get_boost(idx, 'spd') * g.get_active(idx).spd / 1500
        n[f'real_spe_{name}_active'] = g.get_boost(idx, 'spe') * g.get_active(idx).spe / 1500

        n[f'boost_atk_{name}_active'] = (g.get_boost(idx, 'atk') + 6) / 12
        n[f'boost_def_{name}_active'] = (g.get_boost(idx, 'def') + 6) / 12
        n[f'boost_spa_{name}_active'] = (g.get_boost(idx, 'spa') + 6) / 12
        n[f'boost_spd_{name}_active'] = (g.get_boost(idx, 'spd') + 6) / 12
        n[f'boost_spe_{name}_active'] = (g.get_boost(idx, 'spe') + 6) / 12

        # TODO:
        # n[f'used_protect_{name}_active'] =
        # n[f'is_leech_seeded_{name}_active']
        # n[f'is_flying_{name}_active']
        # n[f'is_underground_{name}_active']
        n[f'is_recharging_{name}_active'] = g.get_active(idx).mustrecharge + 2 > g.turn
        # n[f'is_charging_{name}_active']

        for s in STATUS:
            n[f'is_{s}_{name}_active'] = s in g.get_active(idx).status

        for t in TYPES:
            n[f'type_{t.lower()}_{name}_active'] = t in g.get_active(idx).types

        moves = [ x for x in g.get_active(idx).moves.values() ]
        for m in range(0,4):
            mv = moves[m]
            if m < len(moves):
                power = mv.power
                # TODO: if moves[m].name == "earthquake" && enemy isdiggign:
                #
                n[f'move{m}_power_{name}_active'] = power
                n[f'move{m}_pp_{name}_active'] = mv.pp / mv.pp_max
                n[f'move{m}_acc_{name}_active'] = mv.accuracy
                # TODO: n[f'move{m}_crit_{name}_active'] = moves[m].accuracy

        if name == 'player':
            pass
            # use full information of player

    for key in n:
        if type(n[key]) == bool:
            n[key] = 1 if n[key] else 0
    return n
