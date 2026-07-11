from roles.base import Role
from game import texts

class Hunter(Role):
    camp = texts.VILLAGERS
    character_value = 3

    def on_death(self, game, player):
        candidates = [p for p in game.players if p.alive and p.id != player.id]
        
        if candidates:
            suspicion_row = game.suspicion.get_accusation_scores(player.id)
            target = max(candidates, key=lambda p: suspicion_row[p.id])

            if suspicion_row[target.id] < game.params.hunter_shot_threshold:
                game.log(texts.HUNTER_NO_SHOT)
                return

            game.log(texts.HUNTER_SHOT.format(target_id=target.id, role_name=target.role.__class__.__name__))
            
            game.kill_player(target)