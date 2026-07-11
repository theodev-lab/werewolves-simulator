from dataclasses import dataclass

ROLE_COUNTS = {
    "thief": 1,
    "cupid": 1,
    "seer": 1,
    "wolf": 3,
    "little_girl": 1,
    "witch": 1,
    "villager": 4,
    "hunter": 1
}

@dataclass(frozen=True)
class SimulationParameters:
    alpha: float = 0.15
    vote_noise: float = 0.2
    grudge_immediate_weight: float = 0.5
    co_vote_beta: float = 0.3
    co_vote_association_threshold: float = 0.6
    co_vote_association_weight: float = 0.4
    convince_role_value_weight: float = 0.1
    suspicion_role_value_weight: float = 0.1
    wolf_to_wolf_suspicion_resistance: float = 0.15
    hunter_shot_threshold: float = 0.5
    witch_kill_threshold: float = 0.5

DEFAULT_PARAMETERS = SimulationParameters()
USE_SHERIFF = 1
N_GAMES = 1
SEED = 42
