from roles.base import Role
from game import texts
from config import HUNTER_SHOT_THRESHOLD

class Hunter(Role):
    camp = texts.VILLAGERS

    def on_death(self, game, player):
        suspicion_row = game.suspicion.get_suspicion_scores(player.id)
        
        lover = game.get_lover(player)
        candidates = [candidate for candidate in game.alive_players() if candidate is not player and candidate is not lover and suspicion_row[candidate.id] >= HUNTER_SHOT_THRESHOLD]
        target = player.choose_by_suspicion(game, candidates, hesitate=False)

        if target is None:
            game.log(texts.HUNTER_NO_SHOT)

            return

        game.log(texts.HUNTER_SHOT.format(target_id=target.id, role_name=target.role.__class__.__name__))

        game.kill_player(target)
