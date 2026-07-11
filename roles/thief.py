import random

from game import texts
from roles.base import Role
from roles.villager import Villager

class Thief(Role):
    def on_night(self, game, player):
        if game.current_day != 1:
            return

        game.log(texts.THIEF_TURN)

        choices = list(range(len(game.remaining_roles)))

        if not all(role.camp == texts.WOLVES for role in game.remaining_roles):
            choices.append(None)

        chosen_role_index = random.choice(choices)

        if chosen_role_index is None:
            player.role = Villager()
            game.log(texts.SERVER_THIEF_KEEP.format(role_name=player.role.__class__.__name__))
            return

        player.role, game.remaining_roles[chosen_role_index] = game.remaining_roles[chosen_role_index], player.role
        game.log(texts.SERVER_THIEF_SWAP.format(role_name=player.role.__class__.__name__))