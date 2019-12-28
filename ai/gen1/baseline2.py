import lib.gamestate as gs

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
    percent_dmg = min(defder.hp, 0.9*(((2*atker.level)/5+2)*move.power*atk/defense/50+2)*Type/defder.maxhp)
    does_kill = percent_dmg == defder.hp
    return percent_dmg, does_kill


def get_value(attacker, target, move) -> (float, bool):
    value = 0
    stuck = False
    percent_dmg, does_kill = damage_calc(attacker, target, move)
    value += percent_dmg
    if does_kill:
        stuck = True
        target.fainted = True
    if move.sleep_opp:
        stuck = True
    if move.is_explosion:
        value -= attacker.hp
        stuck = True
        attacker.fainted = True
    if move.recovers_health:
        value += min(0.5, 1-attacker.hp)
    if move.drains_health:
        value += min(1-attacker.hp, percent_dmg/2)
    if move.has_recoil:
        value -= min(attacker.hp, percent_dmg*target.maxhp/attacker.maxhp/4)
        if attacker.hp < percent_dmg*target.maxhp/attacker.maxhp/4:
            attacker.fainted = True

    return value, stuck


def simulate(ally, opp, ally_move=None, opp_move=None) -> float:
    """
    Simulates the next turn given the move predictions based on simulation and
    change in health % for opp and ally, outputs change in opp % - change in
    ally %
    """
    value = 0
    faster = ally.spe > opp.spe
    bad = ["frozen", "sleeping"]
    ally_stuck = [s in ally.status for s in bad] or ally.mustrecharge
    opp_stuck = [s in opp.status for s in bad] or opp.mustrecharge
    ally_stuck |= ally_move and ally_move.is_protect and ally.used_protect
    opp_stuck |= opp_move and opp_move.is_protect and opp.used_protect

    if (ally_move and ally_move.is_protect and not ally.used_protect) or (opp_move and opp_move.is_protect and not opp.used_protect):
        ally_stuck = True
        opp_stuck = True

    if faster and ally_move and not ally_stuck:
        delta_value, delta_stuck = get_value(ally, opp, ally_move)
        value += delta_value
        opp_stuck |= delta_stuck
    elif not faster and opp_move and not opp_stuck:
        delta_value, delta_stuck = get_value(opp, ally, opp_move)
        value += delta_value
        ally_stuck |= delta_stuck

    if not faster and ally_move and not ally_stuck:
        delta_value, delta_stuck = get_value(ally, opp, ally_move)
        value += delta_value
        opp_stuck |= delta_stuck
    elif faster and opp_move and not opp_stuck:
        delta_value, delta_stuck = get_value(opp, ally, opp_move)
        value += delta_value
        ally_stuck |= delta_stuck

    for pair in ((ally, opp), (opp, ally)):
        player, other = pair
        if player.is_poisoned and not player.fainted:
            value -= min(12/player.maxhp, player.hp)
            player.fainted |= player.hp*player.maxhp <= 12
        if player.is_burned and not player.fainted:
            value -= min(6/player.maxhp, player.hp)
            player.fainted |= player.hp*player.maxhp <= 6
        if player.is_leech_seeded and not player.fainted and not other.fainted:
            value -= min(6/player.maxhp, player.hp) + min(6/other.maxhp, 1-other.hp)

    return value


def choose_move(state) -> int:
    best_option = 0
    best_value = -1000

    ally = state.player_idx
    opp = ally ^ 1

    ally_moves = state.players[ally]
    opp_moves = state.players[opp]
    ally_active = state.get_active(ally)
    opp_active = state.get_active(opp)

    for move in ally_moves:
        temp_best = min([simulate(ally_active, opp_active, move, opp_move) for opp_move in opp_moves])
        if temp_best > best_value:
            best_value = temp_best
            best_option = ally_moves.index(move)+1
        temp_best = min([simulate(ally_active, opp_active, move) for pkmn in opp.party if pkmn != opp_active and not pkmn.faint])
        if temp_best > best_value:
            best_value = temp_best
            best_option = ally_moves.index(move)+1

    options = [pkmn for pkmn in ally.party if pkmn != ally_active and not pkmn.faint]
    for pkmn in options:
        temp_best = min([simulate(pkmn, opp_active, opp_move) for opp_move in opp_moves])
        if temp_best > best_value:
            best_value = temp_best
            best_option = options.index(pkmn) + 5
        temp_best = min([simulate(pkmn, opp_pkmn) for opp_pkmn in opp.party if opp_pkmn != opp_active and not opp_pkmn.faint])  # Nani
        if temp_best > best_value:
            best_value = temp_best
            best_option = options.index(pkmn) + 5

    return best_option
