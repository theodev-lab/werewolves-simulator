from roles.base import Role
from game import texts
from config import HUNTER_SHOT_THRESHOLD

class Hunter(Role):
    camp = texts.VILLAGERS

    def on_death(self, game, player):
        candidates = [candidate for candidate in game.players if candidate.alive and candidate.id != player.id]
        
        if candidates:
            suspicion_row = game.suspicion.get_suspicion_scores(player.id)
            target = max(candidates, key=lambda candidate: suspicion_row[candidate.id])

            if suspicion_row[target.id] < HUNTER_SHOT_THRESHOLD:
                game.log(texts.HUNTER_NO_SHOT)
                return

            game.log(texts.HUNTER_SHOT.format(target_id=target.id, role_name=target.role.__class__.__name__))
            
            game.kill_player(target)
