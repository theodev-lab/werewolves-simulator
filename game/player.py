import numpy as np
from config import USE_HESITATION

class Player:
    def __init__(self, id, role, rng):
        self.id = id
        self.role = role
        self.alive = True

        self.beta = rng.gamma(shape=4, scale=0.5)
        self.eta = rng.gamma(shape=4, scale=0.5)

    def choose_by(self, game, candidates, scores, on_zero="abstain", hesitate=True):
        if on_zero not in ("abstain", "uniform"):
            raise ValueError("on_zero must be 'abstain' or 'uniform'")

        if not candidates:
            return None

        candidate_scores = np.array([scores[player.id] for player in candidates], dtype=float)
        weights = np.power(candidate_scores, self.beta)

        total_weight = np.sum(weights)

        if total_weight == 0:
            return game.rng.choice(candidates) if on_zero == "uniform" else None

        if USE_HESITATION and hesitate and game.rng.random() >= candidate_scores.max():
            return None

        probabilities = weights / total_weight

        return game.rng.choice(candidates, p=probabilities)

    def choose_by_trust(self, game, candidates, on_zero="uniform", hesitate=True):
        scores = game.suspicion.get_trust_scores(self.id)

        return self.choose_by(game, candidates, scores, on_zero=on_zero, hesitate=hesitate)

    def choose_by_suspicion(self, game, candidates, on_zero="abstain", hesitate=True):
        scores = game.suspicion.get_suspicion_scores(self.id)

        return self.choose_by(game, candidates, scores, on_zero=on_zero, hesitate=hesitate)
