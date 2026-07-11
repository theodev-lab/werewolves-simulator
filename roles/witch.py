from game import texts
from roles.base import Role

class Witch(Role):
    camp = texts.VILLAGERS
    character_value = 5

    def __init__(self):
        self.life_potion_available = True
        self.death_potion_available = True

    def on_night(self, game, player):
        game.log(texts.WITCH_TURN)

        used_potion = False
        wolf_target = game.dead_this_night[0] if game.dead_this_night else None

        if self.life_potion_available and wolf_target is not None and (wolf_target is player or wolf_target is game.get_lover(player)):
            self.life_potion_available = False
            used_potion = True
            game.log(texts.SERVER_WITCH_SAVE.format(target_id=wolf_target.id))
            game.resurrect_player(wolf_target)

        if self.death_potion_available:
            candidates = [p for p in game.players if p.alive and p.id != player.id]

            if candidates:
                suspicion_row = game.suspicion.get_accusation_scores(player.id)
                target = max(candidates, key=lambda p: suspicion_row[p.id])

                if suspicion_row[target.id] >= game.params.witch_kill_threshold:
                    self.death_potion_available = False
                    used_potion = True
                    game.log(texts.SERVER_WITCH_POISON.format(target_id=target.id))
                    game.kill_player(target)

        if not used_potion:
            game.log(texts.SERVER_WITCH_NO_ACTION)