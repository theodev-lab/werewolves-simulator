from game.debate import debate_phase
from game import texts
from roles import Cupid, LittleGirl, Seer, Sheriff, Thief, Witch

def role_turn(game, RoleClass):
    players = game.alive_players() + game.dead_this_night

    for player in players:
        if isinstance(player.role, RoleClass):
            player.role.on_night(game, player)

def wolves_turn(game):
    game.log(texts.WOLVES_TURN)
  
    villagers = [player for player in game.players if player.role.camp == texts.VILLAGERS and player.alive]
  
    if villagers:
        target = game.rng.choice(villagers) # TODO: il faudrait faire devenir les loups intelligents : ils vont éliminer le joueur qui accuse/vote le plus contre des loups en se basant sur l'historique des votes et des actions
        game.log(texts.SERVER_WOLVES_TARGET.format(target_id=target.id))
        game.kill_player(target)

def resolve_death_effects(game):
    death_index = 0

    while death_index < len(game.dead_this_night):
        player = game.dead_this_night[death_index]
        death_index += 1

        # TODO: il faudra revoir la mécanique d'élection du maire
        # if player is game.sheriff and player.alive == False:
        #     Sheriff.appoint_successor(game, get_most_convincing_candidates(game.alive_players()))

        player.role.on_death(game, player)

    game.dead_this_night = []
            
def voting_process(game):
    vote_counts = {}
    
    for player in game.alive_players():
        target = player.vote(game, game.suspicion.get_suspicion_scores(player.id))

        if target is None:
            continue

        vote_counts[target] = vote_counts.get(target, 0) + player.vote_weight 
    
    if not vote_counts:
        return

    target = max(vote_counts, key=vote_counts.get)

    tied_targets = [player for player, count in vote_counts.items() if count == vote_counts[target]]

    # TODO: Gérer les égalités de votes (si c'est le premier tour on élimine personne, sinon c'est le maire qui décide)
    if len(tied_targets) > 1:
        return

    target = tied_targets[0]

    game.log(texts.VOTE_ELIMINATION.format(target_id=target.id, role_name=game.players[target.id].role.__class__.__name__))

    game.kill_player(game.players[target.id])

def night_phase(game):
    game.log(f"\n{texts.NIGHT_START}")

    role_turn(game, Thief)
    role_turn(game, Cupid)
    role_turn(game, LittleGirl)
    role_turn(game, Seer)
    wolves_turn(game)
    role_turn(game, Witch)

def day_phase(game):
    if not game.dead_this_night:
        game.log(texts.DAY_NO_DEATH)
    else:
        dead_infos = [texts.DEAD_PLAYER.format(player_id=player.id, role_name=player.role.__class__.__name__) for player in game.dead_this_night]
        dead_str = dead_infos[0] if len(dead_infos) == 1 else texts.DEAD_PLAYERS_JOIN.format(players=", ".join(dead_infos[:-1]), last_player=dead_infos[-1])
        game.log(texts.DAY_DEATHS.format(dead_players=dead_str))
        
    resolve_death_effects(game)
    
    over, _ = game.is_over()
    
    if not over:
        debate_phase(game)
        voting_process(game)

    resolve_death_effects(game)
