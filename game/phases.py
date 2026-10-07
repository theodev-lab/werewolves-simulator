from game.debate import debate_phase
from game import texts
from game.suspicion import SuspicionManager
from roles import Cupid, LittleGirl, Seer, Thief, Witch
from config import USE_SHERIFF
from game.sheriff import elect_sheriff, choose_successor, break_vote_tie, get_vote_weight

def role_turn(game, RoleClass):
    players = game.alive_players() + game.dead_this_night

    for player in players:
        if isinstance(player.role, RoleClass):
            player.role.on_night(game, player)

def wolves_turn(game):
    if not any(player.alive and player.role.camp == texts.WOLVES for player in game.players):
        return

    game.log(texts.WOLVES_TURN)

    # TODO: gérer la protection de l'amoureux d'un loup lors du choix de la victime.
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

        player.role.on_death(game, player)

    game.dead_this_night = []

    if game.sheriff is not None and not game.sheriff.alive:
        choose_successor(game, game.sheriff)

def voting_process(game):
    vote_counts = {}

    for player in game.alive_players():
        lover = game.get_lover(player)
        candidates = [candidate for candidate in game.alive_players() if candidate is not player and candidate is not lover]
        target = player.choose_by_suspicion(game, candidates)

        if target is None:
            continue

        vote_counts[target] = (vote_counts.get(target, 0) + get_vote_weight(game, player))

    if not vote_counts:
        game.log(texts.VOTE_NO_ELIMINATION)

        return

    max_votes = max(vote_counts.values())

    tied_targets = [target for target, votes in vote_counts.items() if votes == max_votes]

    if len(tied_targets) == 1:
        target = tied_targets[0]
    else:
        target = break_vote_tie(game, tied_targets)

        if target is None:
            game.log(texts.VOTE_NO_ELIMINATION)

            return

    game.log(texts.VOTE_ELIMINATION.format(target_id=target.id, role_name=target.role.__class__.__name__))

    game.kill_player(target)

def night_phase(game):
    game.log(f"\n{texts.NIGHT_START}")

    role_turn(game, Thief)

    if game.current_day == 1:
        game.suspicion = SuspicionManager(game.players)

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

        if USE_SHERIFF and game.current_day == 1 and game.sheriff is None:
            elect_sheriff(game)

        voting_process(game)

    resolve_death_effects(game)
