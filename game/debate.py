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
            if action != "stay_silent":
                game.suspicion.suspicion_update(player.id, target.id, game.suspicion.compute_likelihood_ratio(TARGET_ACTIONS[action]) ** game.suspicion.get_trust_scores(player.id)[speaker.id])

def debate_phase(game):
    action_count = get_action_count(game)

    for _ in range(action_count):
        speaker = get_next_speaker(game)

        if speaker is None:
            break

        action = choose_action(game, speaker)

        if action == "stay_silent":
            target = None
        else:
            mode = "least_suspicious" if action == "defend" else "most_suspicious"
            target = speaker.choose_target(game, game.suspicion.get_suspicion_scores(speaker.id), mode=mode)

            if target is None:
                continue

        propagate_information(game, speaker, action, target)
