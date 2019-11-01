import random

def calc_damage(power, attack, defense = 175, multiplier):
    return power*attack/(defense*2)

# NEED to get typing system for multiplier :D

def factor_calc(effect, chance, E_Hp, Spd_Ratio, A_BestMove, E_BestMove):
    factor = 0
    if effect == 'Toxic':
        factor = 60*E_Hp
    elif effect == "Psn":
        factor = 24*E_Hp
    elif effect == "Brn":
        factor = 12 + E_BestPhys
        if move_first:
            factor *= 1.5
        factor *= E_Hp
    elif effect == "Paralyze":
        factor = 3*A_BestMove 
    elif effect == "Slp":
        factor = 2.5*A_BestMove
    elif effect == "Frz":
        factor = 4**A_BestMove
    elif effect == "Flinch":
        if Spd_Ratio > 1:
            factor = A_BestMove
    return factor*chance

def consider_moves(enemy, ally):
    scores = []
    damages = []
    enemy_scores = []
    enemy_damages = []      
    enemy_fatals = []
    enemy_fatal = False

    enemy_attack = 175
    enemy_defense = 175
    enemy_special = 175
    speed = max_enemy_speed

    threshold = 5

    if enemy.name in enemy_pkmns.keys:
        if attack in enemy_pkmns[enemy.name].keys:
            enemy_attack = enemy_pkmns[enemy.name][attack]
        if defense in enemy_pkmns[enemy.name].keys:
            enemy_defense = enemy_pkmns[enemy.name][defense]
        if special in enemy_pkmns[enemy.name].keys:
            enemy_special = enemy_pkmns[enemy.name][special]
        if moves in enemy_pkmns[enemy.name].keys:
            for move in enemy_pkmns[enemy.name][moves]:
                enemy_damages.append(calc_damage(move.power, enemy_attack, defense)
                if enemy_damages[-1] > ally.hp:
                    enemy_fatals.append(True)
                    enemy_fatal = True
                else:
                    enemy_fatals.append(False)
                if move.effect: #if the move has a special effect attached
                    if move.effect == 'confuse':
                        extra = 2*max(enemy_damages)*chance
                    else:
                        extra = factor_calc(effect, chance, E_Hp, ally.speed/speed, max(enemy_damages), max(damages))
                    enemy_scores.append(dmg + extra)
    enemy_damages.append(calc_damage(90, enemy_somethingattack, ally.somethingdefense)) 
    if enemy_damages[-1] > ally.hp:
        enemy_fatals.append(True)
        enemy_fatal = True
    else:
        enemy_fatals.append(False)    
    enemy_scores.append(enemy_damages[-1])      

    #^because we can track whether a move is special or phys based on typing apparently. 
    #So we need to do the above for a 90 damage move of each type the pokemon has.

    fatals = []
    for move in ally.moves:
        dmg = calc_damage(move.power, ally.attack, defense, multiplier)
        if dmg > enemy.hp:
            fatals.append(True)
        else:
            fatals.append(False)
        if move.effect: #if the move has a special effect attached
            if move.effect == 'confuse':
                extra = max(damages)*chance
            else:
                extra = factor_calc(effect, chance, E_Hp, speed/ally.speed, max(damages), max(enemy_damages))
            scores.append(dmg + extra)
    first = False
    if ally.speed>speed:
        first = True        

def choose_move(gamestate):
    options = []
    consider_moves(enemy, ally)              
    first = False
    find_other = False
    if ally.speed > speed:
        first = True

    if enemy_fatal:
        if not first and ally.health > threshold:
            find_other = True
        if not first and ally.health <= threshold:
            return moves[scores.index(max(scores))]
        if first and not fatals:
            if ally.health > threshold:
                find_other = True
    if fatals:
        f = [a for a in range(len(ally.moves)) if fatals[a]]
        options.append(ally.moves[f[random.randint(0, len(f)-1)]])

    bad_moves = False

    if max(scores) < max(enemy_scores):
        find_other = True
    E = [[a]*(scores[a]-enemy_scores) for a in range(len(scores)) if scores[a] - max(enemy_scores) > 0]
    if E:
        option.append(ally.moves[random.choice(E)])
    #Note: not sure if want to just use max score or smt
    else:
        option.append(ally.moves[scores.index(max(scores))])
        bad_moves = True
    damage = damages[ally.moves.index(option[0])]
        
    if find_other:
        p_move = enemy_pkmns[enemy.name][moves][enemy_scores.index(max(enemy_scores))]
        p_damage = enemy_damages[enemy_scores.index(max(enemy_scores))]
        switch_scores = []
        for pkmn in ally_pokemon:
            switch_scores.append(0)
            switch_scores[-1] += p_damage
            switch_scores[-1] -= calc_damage(p_move.power, enemy.defense, pkmn.defense, multiplier)
            consider_moves(enemy, pkmn)
            #make sure later to account for hp lost during switch time
            if pkmn.spped > speed:
                first = True
            if not first and enemy_fatal:
                switch_scores[-1] = 0
                continue
            elif first and enemy_fatal and not fatals:
                switch_scores[-1] = 0
                continue
            else:
                switch_scores += max(scores) - max(enemy_scores)
        E = [[a]*switch_scores[a] for a in range(len(switch_scores)) if switch_scores[a] > 0]
        if E:
            option.append(ally_pokemon[random.choice(E)]
            if option[0] < 0:
                option.pop(0)
    if option[0] in ally.moves and len(enemy_pkmn) > 1 and not bad_moves:
        enemy_switches = []
        for pkmn in enemy_pkmn:
            enemy_switches.append(0)
            if enemy_pkmn == enemy:
                continue
            enemy_switches[-1] -= damage
            consider_moves(pkmn, ally)
            #remember to take into account damage taken by first move during switch time
            if fatals and first:
                continue
            if enemy_fatals and not first:
                enemy_switches[-1] += 10000
                continue
            if enemy_fatals and first:
                enemy_switches[-1] += 10000
                enemy_switches -= max(damages)
                continue
            enemy_switches[-1] += max(enemy_damages) - max(damages)
        E = [enemy_switches[a] for a in range(len(enemy_switches)) if enemy_switches[a] > 0]
        if not E:
            break
        p_switch = enemy_pkmn[enemy_switches.index(max(enemy_switches))]
        consider_moves(p_switch, ally)
        find_other = False
        if max(damages)*2 > 100 and (first or not enemy_fatals):
            options.append(moves[damages.index(max(damages))])
        else:
            options.append(moves[damages.index(max(damages))])
            find_other = True
        if find_other:
            double_switch = []
            for pkmn in ally_pkmn:
                consider_moves(p_switch, pkmn)
                double_switch.append(max(enemy_scores)-max(scores))
            O_wo = [[a]*double_switch[a] for a in range(len(double_switch)) if double_switch[a] > 0]
            if O_wo:
                options.append(ally_pkmn[random.choice(E)])
                if options[-2] < 0:
                    options.pop(-2)
    return options #then you can just use best or randomize or whatever

