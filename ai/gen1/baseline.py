import lib.gamestate as gs
import lib.choice as choice

# note that the output of main function is a single integer representing the
# move made
# 1-4 are the moves
# 5-9 are the switches
# Both of the above are in order as stored in gamestate


def damage_calc(atker: gs.Pokemon,
                defder: gs.Pokemon,
                move: gs.Move) -> (float, bool):
    """
    Takes a single instance of one pokemon attacking another Calculates
    predicted % damage using the assumption of RANDOM = 0.9 Outputs predicted
    damage and bool indicating whether defending pokemon is predicted to faint
    """

    if move.category == "Physical":
        atk = atker.atk
        defense = defder.defense
    else:
        atk = atker.spa
        defense = defder.spd

    Type = 1  # TODO
    percent_dmg = min(defder.hp_percent, 0.9*(((2*atker.level)/5+2)*move.power*atk/defense/50+2)*Type/defder.maxhp)
    does_kill = percent_dmg == defder.hp_percent
    print("!@" + str(percent_dmg))
    return percent_dmg, does_kill


def get_value(attacker, target, move) -> (float, bool):
    value = 0
    stuck = False
    percent_dmg, does_kill = damage_calc(attacker, target, move)
    value += percent_dmg
    if does_kill:
        stuck = True
        target.faint = True
    if move.status == "slp":
        stuck = True
    if move.name == "explosion":
        value -= attacker.hp
        stuck = True
        attacker.faint = True
    #if move.recovers_health:
    #    value += min(0.5, 1-attacker.hp_percent)
    if move.drain:
        value += min(1-attacker.hp_percent, percent_dmg/2)
    if move.recoil:
        value -= min(attacker.hp_percent, percent_dmg*target.maxhp/attacker.maxhp/4)
        if attacker.hp < percent_dmg*target.maxhp/4:
            attacker.faint = True

    print(value)
    return value, stuck


def simulate(ally, oppo, ally_move=None, oppo_move=None) -> float:
    """
    Simulates the next turn given the move predictions based on simulation and
    change in health % for oppo and ally, outputs change in oppo % - change in
    ally %
    """
    value = 0
    faster = ally.spe > oppo.spe
    bad = ["frozen", "sleeping"]
    ally_stuck = len([s for s in ally.status if s in bad]) > 0  # or ally.is_mustrecharge()
    oppo_stuck = len([s for s in oppo.status if s in bad]) > 0  # or oppo.is_mustrecharge()
    # ally_stuck = ally_stuck or (ally_move is not None and ally_move.is_protect() and ally.used_protect())
    # oppo_stuck = oppo_stuck or (oppo_move is not None and oppo_move.is_protect() and oppo.used_protect())

    print(len([s for s in ally.status if s in bad]) > 0 )

    print(ally_stuck, oppo_stuck)

    if (ally_move and ally_move.is_protect and not ally.used_protect) or (oppo_move and oppo_move.is_protect and not oppo.used_protect):
        ally_stuck = True
        oppo_stuck = True

    if faster and ally_move and not ally_stuck:
        delta_value, delta_stuck = get_value(ally, oppo, ally_move)
        value += delta_value
        oppo_stuck |= delta_stuck
    elif not faster and oppo_move and not oppo_stuck:
        delta_value, delta_stuck = get_value(oppo, ally, oppo_move)
        value += delta_value
        ally_stuck |= delta_stuck

    if not faster and ally_move and not ally_stuck:
        delta_value, delta_stuck = get_value(ally, oppo, ally_move)
        value += delta_value
        oppo_stuck |= delta_stuck
    elif faster and oppo_move and not oppo_stuck:
        delta_value, delta_stuck = get_value(oppo, ally, oppo_move)
        value += delta_value
        ally_stuck |= delta_stuck

    for pair in ((ally, oppo), (oppo, ally)):
        player, other = pair
        if player.is_poisoned and not player.faint:
            value -= min(12/player.maxhp, player.hp_percent)
            player.faint |= player.hp <= 12
        if player.is_burned and not player.faint:
            value -= min(6/player.maxhp, player.hp_percent)
            player.faint |= player.hp <= 6
        if player.is_leech_seeded and not player.faint and not other.faint:
            value -= min(6/player.maxhp, player.hp_percent) + min(6/other.maxhp, 1-other.hp_percent)

    return value


def choose_move(state: gs.GameState) -> int:
    best_option = 0
    best_value = -1000

    ally = state.player_idx
    oppo = ally ^ 1

    ally_active = state.players[ally].get_active(True)
    oppo_active = state.players[oppo].get_active()
    ally_moves = [ally_active.moves[move] for move in ally_active.moves]
    oppo_moves = [oppo_active.moves[move] for move in oppo_active.moves]
    ally_team = [state.players[ally].secret[p] for p in state.players[ally].secret]
    oppo_team = [state.players[oppo].team[p] for p in state.players[oppo].team]
    ally_options = [p for p in ally_team if p != ally_active and not p.faint]
    oppo_options = [p for p in oppo_team if p != oppo_active and not p.faint]

    if not state.force_switch:
        for move in ally_moves:
            print(move.name)
            if oppo_moves:
                temp_best = min([simulate(ally_active, oppo_active, move, oppo_move) for oppo_move in oppo_moves])
                print("A")
                print(temp_best)
                if temp_best > best_value:
                    best_value = temp_best
                    best_option = ally_moves.index(move) + 1

            if oppo_options:
                temp_best = min([simulate(ally_active, pkmn, move, None) for pkmn in oppo_options])
                print(temp_best)
                if temp_best > best_value:
                    best_value = temp_best
                    best_option = ally_moves.index(move) + 1

            if not oppo_options and not oppo_moves:
                temp_best = simulate(ally_active, oppo_active, move, None)
                print(temp_best)
                if temp_best > best_value:
                    best_value = temp_best
                    best_option = ally_moves.index(move) + 1

    for pkmn in ally_options:
        print(pkmn.name)
        if oppo_moves:
            temp_best = min([simulate(pkmn, oppo_active, None, oppo_move) for oppo_move in oppo_moves])
            print(temp_best)
            if temp_best > best_value:
                best_value = temp_best
                best_option = ally_team.index(pkmn) + 5

        if oppo_options:
            temp_best = min([simulate(pkmn, oppo_pkmn, None, None) for oppo_pkmn in oppo_options])
            print(temp_best)
            if temp_best > best_value:
                best_value = temp_best
                best_option = ally_team.index(pkmn) + 5

        if not oppo_options and not oppo_moves:
            temp_best = simulate(pkmn, oppo_active)
            print(temp_best)
            if temp_best > best_value:
                best_value = temp_best
                best_option = ally_team.index(pkmn) + 5

    return choice.choice(best_option)
