import numpy as np
from game import texts

class SuspicionManager:
    def __init__(self, players):
        self.players = players
        self.suspicion = np.full((len(self.players), len(self.players)), sum(player.role.camp == texts.WOLVES for player in self.players)) / (len(self.players) - 1)
        self.locked = np.zeros((len(self.players), len(self.players)))

        for i in range(len(self.players)):
            self.lock_cell(i, i, 0)

    def get_suspicion_scores(self, player_id):
        return self.suspicion[player_id]

    def get_trust_scores(self, player_id):
        return 1 - self.suspicion[player_id]

    def lock_cell(self, observer_id, target_id, value):
        self.suspicion[observer_id][target_id] = value
        self.locked[observer_id][target_id] = True

    def compute_likelihood_ratio(self, observation):
        return observation[texts.WOLVES] / observation[texts.VILLAGERS]

    def suspicion_update(self, observer_id, target_id, likelihood_ratio):
        if self.locked[observer_id][target_id]:
            return

        prior = self.suspicion[observer_id][target_id]

        self.suspicion[observer_id][target_id] = (likelihood_ratio * prior) / (1 - prior + likelihood_ratio * prior)
