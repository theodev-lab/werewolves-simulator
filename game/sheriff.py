import numpy as np

from game import texts

def get_candidates(game):
    players = game.alive_players()

    if not players:
        return []

    mean_eta = np.mean([player.eta for player in players])
    candidates = [player for player in players if game.rng.random() < player.eta / (player.eta + mean_eta)]

    if not candidates and players:
        candidates = [game.rng.choice(players)]

    return candidates

def elect_sheriff(game):
    candidates = get_candidates(game)

    if not candidates:
        return

    if len(candidates) == 1:
        game.sheriff = candidates[0]
    else:
        votes = {}

        for voter in game.alive_players():
            target = voter if voter in candidates else voter.choose_by_trust(game, candidates, on_zero="abstain")

            if target is None:
                continue

            votes[target] = votes.get(target, 0) + 1

        highest = max(votes.values())

        game.sheriff = game.rng.choice([p for p in candidates if votes[p] == highest])

    game.log(texts.SHERIFF_ELECTED.format(player_id=game.sheriff.id))

def choose_successor(game, outgoing_sheriff):
    candidates = game.alive_players()

    game.sheriff = outgoing_sheriff.choose_by_trust(game, candidates, hesitate=False)

    if game.sheriff is not None:
        game.log(texts.SHERIFF_SUCCESSOR.format(player_id=game.sheriff.id))

def break_vote_tie(game, tied_players):
    sheriff = game.sheriff

    if sheriff is None or not sheriff.alive:
        return None

    candidates = [p for p in tied_players if p is not sheriff and p is not game.get_lover(sheriff)]

    if not candidates:
        game.log(texts.SHERIFF_NO_KILL)

        return None

    target = sheriff.choose_by_suspicion(game, candidates)

    if target is None:
        game.log(texts.SHERIFF_NO_KILL)

        return None

    game.log(texts.SHERIFF_KILL.format(target_id=target.id, role_name=target.role.__class__.__name__))

    return target

def get_vote_weight(game, player):
    return 2 if player is game.sheriff else 1
