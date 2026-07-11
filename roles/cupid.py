import random

from game import texts
from roles.base import Role

class Cupid(Role):
    camp = texts.VILLAGERS
    character_value = -2

    def on_night(self, game, player):
        if game.current_day != 1:
            return

        game.log(texts.CUPID_TURN)

        lovers = random.sample(game.alive_players(), 2)
        game.set_lovers(lovers[0], lovers[1])
        game.log(texts.SERVER_CUPID_LOVERS.format(lover1_id=lovers[0].id, lover2_id=lovers[1].id))

        game.suspicion.lock_cell(lovers[0].id, lovers[1].id, 0)
        game.suspicion.lock_cell(lovers[1].id, lovers[0].id, 0)