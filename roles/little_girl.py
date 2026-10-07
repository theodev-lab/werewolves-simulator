from game import texts
from roles.base import Role

class LittleGirl(Role):
    camp = texts.VILLAGERS

    def on_night(self, game, player):
        if game.current_day != 1:
            return

        for target in game.players:
            if target.role.camp == texts.WOLVES:
                game.suspicion.lock_cell(player.id, target.id, 1)
