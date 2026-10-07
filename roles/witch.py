from game import texts
from roles.base import Role
from config import WITCH_KILL_THRESHOLD, WITCH_SAVE_THRESHOLD

class Witch(Role):
    camp = texts.VILLAGERS

    def __init__(self):
        self.life_potion_available = True
        self.death_potion_available = True

    def on_night(self, game, player):
        game.log(texts.WITCH_TURN)

        used_potion = False
        wolf_target = game.dead_this_night[0] if game.dead_this_night else None

        lover = game.get_lover(player)
        should_save = False

        if self.life_potion_available and wolf_target is not None:
            if wolf_target is player or wolf_target is lover:
                should_save = True
            else:
                trust_scores = game.suspicion.get_trust_scores(player.id)
                should_save = trust_scores[wolf_target.id] >= WITCH_SAVE_THRESHOLD

        if should_save:
            self.life_potion_available = False
            used_potion = True

            game.log(texts.SERVER_WITCH_SAVE.format(target_id=wolf_target.id))

            game.resurrect_player(wolf_target)

        if self.death_potion_available:
            suspicion_row = game.suspicion.get_suspicion_scores(player.id)

            candidates = [candidate for candidate in game.alive_players() if candidate is not player and candidate is not lover and suspicion_row[candidate.id] >= WITCH_KILL_THRESHOLD]
            target = player.choose_by_suspicion(game, candidates, hesitate=False)

            if target is not None:
                self.death_potion_available = False
                used_potion = True

                game.log(texts.SERVER_WITCH_POISON.format(target_id=target.id))

                game.kill_player(target)

        if not used_potion:
            game.log(texts.SERVER_WITCH_NO_ACTION)
