#note that the output of main function is a single integer representing the move made
#1-4 are the moves
#5-9 are the switches
#Both of the above are in order as stored in gamestate
physical = ["normal", "fighting", "flying", "poison", "ground", "rock", "bug", "ghost", "steel"]

def damage_calc(Pokemon atker, Pokemon defder, Move atk_move) -> [float, bool]:
    '''
    Takes a single instance of one pokemon attacking another
    Calculates predicted % damage using the assumption of RANDOM = 0.9
    Outputs predicted damage and bool indicating whether defending pokemon is predicted to faint
    '''
    result = []
    if atk_move.category == "Physical":
        atk = atker.atk
        defense = defder.defense
    else:
        atk = atker.spa
        defense = defder.spd

    result.append(min(defder.hp*100, 0.9*(((2*atker.level)/5+2)*atk_move.power*atk/defense/50+2)*Type/defder.maxhp*100)) #TODO: Make Type multiplier for type effectiveness
    if result[0] == defder.hp*100:
        result.append(True)
    else:
        result.append(False)
    return result

def simulate(ally, opp, ally_move = None, opp_move = None) -> float:
    '''
    Simulates the next turn given the move predictions
    Based on simulation and change in health % for opp and ally, outputs change in opp % - change in ally %
    '''
    value = 0
    faster = ally.spe > opp.spe
    bad = ["frozen", "sleeping"]
    if [s in ally.status for s in bad] or ally.mustrecharge:
        ally_stuck = True
    else:
        ally_stuck = False
    if [s in opp.status for s in bad] or opp.mustrecharge:
        opp_stuck = True
    else:
        opp_stuck = False
    if (ally_move != None and ally_move.is_protect and not ally.used_protect) or (opp_move != None and opp_move.is_protect and not opp.used_protect):
        ally_stuck = True
        opp_stuck = True
    if (ally_move != None and ally_move.is_protect and ally.used_protect):
        ally_stuck = True
    if (opp_move != None and opp_move.is_protect and opp.used_protect):
        opp_stuck = True

    if faster and ally_move != None and not ally_stuck:
        result = damage_calc(ally, opp, ally_move)
        value += result[0]
        if result[1]:
            opp_stuck = True
            opp.fainted = True
        extra = 0
        if ally_move.sleep_opp:
            opp_stuck = True
        if ally_move.is_explosion:
            extra -= ally.hp*100
            opp_stuck = True
            ally.fainted = True
        if ally_move.recovers_health:
            extra += min(50, (1-ally.hp)*100)
        if ally_move.drains_health:
            extra += min((1-ally.hp)*100, result[0]/2)
        if ally_move.has_recoil:
            extra -= min(ally.hp*100, result[0]*opp.maxhp/4/ally.maxhp)
            if ally.hp*100 < result[0]*opp.maxhp/4/ally.maxhp:
                ally.fainted = True
        value += extra
    elif not faster and opp_move != None and not opp_stuck:
        result = damage_calc(opp, ally, opp_move)
        value -= result[0]
        if result[1]:
            ally_stuck = True
            ally.fainted = True
        extra = 0
        if opp_move.sleep_opp:
            ally_stuck = True
        if opp_move.is_explosion:
            extra -= opp.hp*100
            ally_stuck = True
            opp.fainted = True
        if opp_move.recovers_health:
            extra += min(50, (1-opp.hp)*100)
        if opp_move.drains_health:
            extra += min((1-opp.hp)*100, result[0]/2)
        if opp_move.has_recoil:
            extra -= min(opp.hp*100, result[0]*ally.maxhp/4/opp.maxhp)
            if opp.hp*100 < result[0]*ally.maxhp/4/opp.maxhp:
                opp.fainted = True
        value -= extra

    if not faster and ally_move != None and not ally_stuck:
        result = damage_calc(ally, opp, ally_move)
        value += result[0]
        if result[1]:
            opp_stuck = True
        extra = 0
        if ally_move.sleep_opp:
            opp_stuck = True
        if ally_move.is_explosion:
            extra -= ally.hp*100
            opp_stuck = True
        if ally_move.recovers_health:
            extra += min(50, (1-ally.hp)*100)
        if ally_move.drains_health:
            extra += min((1-ally.hp)*100, result[0]/2)
        if ally_move.has_recoil:
            extra -= min(ally.hp*100, result[0]*opp.maxhp/4/ally.maxhp)
        value += extra
    elif faster and opp_move != None and not opp_stuck:
        result = damage_calc(opp, ally, opp_move)
        value -= result[0]
        if result[1]:
            ally_stuck = True
        extra = 0
        if opp_move.sleep_opp:
            ally_stuck = True
        if opp_move.is_explosion:
            extra -= opp.hp*100
            ally_stuck = True
        if opp_move.recovers_health:
            extra += min(50, (1-opp.hp)*100)
        if opp_move.drains_health:
            extra += min((1-opp.hp)*100, result[0]/2)
        if opp_move.has_recoil:
            extra -= min(opp.hp*100, result[0]*ally.maxhp/4/opp.maxhp)
        value -= extra

    if ally.is_poisoned and not ally.fainted:
        value -= min(12, ally.hp*100)
        if ally.hp*100 < 12:
            ally.fainted = True
    if ally.is_burned and not ally.fainted:
        value -= min(6, ally.hp*100)
        if ally.hp*100 < 6:
            ally.fainted = True
    if opp.is_poisoned and not opp.fainted:
        value += min(12, opp.hp*100)
        if opp.hp*100 < 12:
            opp.fainted = True
    if ally.is_burned and not opp.fainted:
        value += min(6, opp.hp*100)
        if opp.hp*100 < 6:
            opp.fainted = True
    if ally.is_leech_seeded and not ally.fainted and not opp.fainted:
        value -= min(6, ally.hp*100) + min(6, (1-opp.hp)*100)
    if opp.is_leech_seeded and not ally.fainted and not opp.fainted:
        value += min(6, opp.hp*100) + min(6, (1-ally.hp)*100)

    return value

def main(state) -> int:
    best_option = 0
    best_value = -1000

    opp_moves = opp_active_known_moves
    for t in opp_active.types:
        temp = Move(gen)
        temp.type = t
        if t.lower() in physical:
            temp.category = "Physical"
        else:
            temp.category = "Special"

    for move in ally_moves:
        temp_best = min([simulate(ally = ally_active, opp = opp_active, ally_move = move, opp_move = opp_move) for opp_move in opp_moves])
        if temp_best > best_value:
            best_value = temp_best
            best_option = ally_moves.index(move)+1
        temp_best = min([simulate(ally = ally_active, opp = pkmn, ally_move = move) for pkmn in opp.party if pkmn != opp_active and not pkmn.faint])
        if temp_best > best_value:
            best_value = temp_best
            best_option = ally_moves.index(move)+1
        
    
    options = [pkmn for pkmn in ally.party if pkmn != ally_active and not pkmn.faint]
    for pkmn in options:
        temp_best = min([simulate(ally = pkmn, opp = opp_active, opp_move = opp_move) for opp_move in opp_moves])
        if temp_best > best_value:
            best_value = temp_best
            best_option = options.index(pkmn) + 5
        temp_best = min([simulate(ally = pkmn, opp = opp_pkmn) for opp_pkmn in opp.party if opp_pkmn != opp_active and not opp_pkmn.faint])
        if temp_best > best_value:
            best_value = temp_best
            best_option = options.index(pkmn) + 5

    return best_option
