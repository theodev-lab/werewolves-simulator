import numpy as np

from config import DEBATE_ACTIONS_LAMBDA
from game import texts

ACTIONS = {
    "accuse": {texts.WOLVES: 0.30, texts.VILLAGERS: 0.40},
    "defend": {texts.WOLVES: 0.10, texts.VILLAGERS: 0.20},
    "follow": {texts.WOLVES: 0.35, texts.VILLAGERS: 0.25},
    "stay_silent": {texts.WOLVES: 0.25, texts.VILLAGERS: 0.15}
}

TARGET_ACTIONS = {
    "accuse": {texts.WOLVES: 0.60, texts.VILLAGERS: 0.40},
    "defend": {texts.WOLVES: 0.30, texts.VILLAGERS: 0.70},
    "follow": {texts.WOLVES: 0.55, texts.VILLAGERS: 0.45}
}

def get_action_count(game):
    return game.rng.poisson(DEBATE_ACTIONS_LAMBDA)

def get_next_speaker(game):
    speakers = game.alive_players()

    if not speakers:
        return None

    weights = np.array([player.eta for player in speakers])

    return game.rng.choice(speakers, p=weights / np.sum(weights))

def choose_action(game, speaker):
    camp = texts.WOLVES if speaker.role.camp == texts.WOLVES else texts.VILLAGERS

    probabilities = [ACTIONS[action][camp] for action in ACTIONS]
    action_index = game.rng.choice(len(ACTIONS), p=probabilities)

    return list(ACTIONS.keys())[action_index]

def propagate_information(game, speaker, action, target=None):
    for player in game.alive_players():
        if player.id != speaker.id:
            # Update suspicion toward the speaker
            game.suspicion.suspicion_update(player.id, speaker.id, game.suspicion.compute_likelihood_ratio(ACTIONS[action]))

            # Update suspicion toward the target if applicable
            if action != "stay_silent" and target is not speaker:
                game.suspicion.suspicion_update(player.id, target.id, game.suspicion.compute_likelihood_ratio(TARGET_ACTIONS[action]) ** game.suspicion.get_trust_scores(player.id)[speaker.id])

def debate_phase(game):
    action_count = get_action_count(game)

    accusations = {}

    for _ in range(action_count):
        speaker = get_next_speaker(game)

        if speaker is None:
            break

        action = choose_action(game, speaker)
        lover = game.get_lover(speaker)
        target = None

        if action == "accuse":
            candidates = [player for player in game.alive_players() if player is not speaker and player is not lover]
            target = speaker.choose_by_suspicion(game, candidates)

            if target is not None:
                accusations[speaker] = target
        elif action == "defend":
            candidates = [player for player in game.alive_players() if player in accusations.values()]
            target = speaker.choose_by_trust(game, candidates, on_zero="abstain")
        elif action == "follow":
            candidates = [author for author, accused in accusations.items() if author is not speaker and author.alive and accused.alive and accused is not speaker and accused is not lover]
            author = speaker.choose_by_trust(game, candidates, on_zero="abstain")
            target = accusations.get(author)

        if target is None and action != "stay_silent":
            continue

        propagate_information(game, speaker, action, target)
