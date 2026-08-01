import numpy as np

class Player:
    def __init__(self, id, role, rng):
        self.id = id
        self.role = role
        self.alive = True
        self.vote_weight = 1

        self.beta = rng.gamma(shape=4, scale=0.5)
        self.eta = rng.gamma(shape=4, scale=0.5)

    def choose_target(self, game, suspicion_row, mode="most_suspicious"):
        lover = game.get_lover(self)
        candidates = [player for player in game.players if player.alive and player.id != self.id and (mode == "least_suspicious" or player is not lover)]

        if not candidates:
            return None

        scores = np.array([suspicion_row[player.id] for player in candidates], dtype=float)

        if mode == "least_suspicious":
            scores = 1 - scores

        weights = np.power(scores, self.beta)
        total_weight = np.sum(weights)

        if total_weight == 0:
            return None

        probabilities = weights / total_weight

        return game.rng.choice(candidates, p=probabilities)

    def vote(self, game, suspicion_row):
        return self.choose_target(game, suspicion_row, mode="most_suspicious")
