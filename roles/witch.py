from game import texts
from roles.base import Role
from config import WITCH_KILL_THRESHOLD

class Witch(Role):
    camp = texts.VILLAGERS

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
            candidates = [candidate for candidate in game.players if candidate.alive and candidate.id != player.id]

            if candidates:
                suspicion_row = game.suspicion.get_suspicion_scores(player.id)
                target = max(candidates, key=lambda candidate: suspicion_row[candidate.id])

                if suspicion_row[target.id] >= WITCH_KILL_THRESHOLD:
                    self.death_potion_available = False
                    used_potion = True
                    game.log(texts.SERVER_WITCH_POISON.format(target_id=target.id))
                    game.kill_player(target)

        if not used_potion:
            game.log(texts.SERVER_WITCH_NO_ACTION)
