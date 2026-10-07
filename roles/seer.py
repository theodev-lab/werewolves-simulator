from game import texts
from roles.base import Role

class Seer(Role):
    camp = texts.VILLAGERS

    def on_night(self, game, player):
        game.log(texts.SEER_TURN)

        candidates = [target for target in game.alive_players() if target.id != player.id and not game.suspicion.locked[player.id][target.id]]

        if not candidates:
            return

        target = player.choose_by_suspicion(game, candidates, on_zero="uniform", hesitate=False)

        if target is None:
            return

        game.log(texts.SERVER_SEER_SPY.format(target_id=target.id, role_name=target.role.__class__.__name__))

        suspicion = 1 if target.role.camp == texts.WOLVES else 0

        game.suspicion.lock_cell(player.id, target.id, suspicion)
