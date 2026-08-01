import numpy as np

from game.player import Player
from game.suspicion import SuspicionManager
from game.phases import night_phase, day_phase
from game import texts
from roles import ROLE_MAP, Villager
from config import N_GAMES

class Game:
	def __init__(self, role_counts, seed=None):
		self.role_counts = role_counts
		self.rng = np.random.default_rng(seed)
		self.players = self.init_players()
		
		self.suspicion = SuspicionManager(self.players)
		
		self.history = []
		self.dead_this_night = []
		self.current_day = 0
		self.sheriff = None
		self.lovers = None
		
	def log(self, message):
		if N_GAMES == 1:
			self.history.append(message)
	
	def init_players(self):
		roles_deck = []
  
		for role_name, count in self.role_counts.items():
			RoleClass = ROLE_MAP[role_name]
			roles_deck.extend([RoleClass() for _ in range(count)])

		if self.role_counts.get("thief", 0) > 0:
			roles_deck.extend([Villager() for _ in range(2)])
		
		self.rng.shuffle(roles_deck)

		dealt_roles = roles_deck[:sum(self.role_counts.values())]
		self.remaining_roles = roles_deck[sum(self.role_counts.values()):]
  
		return [Player(i, role, self.rng) for i, role in enumerate(dealt_roles)]

	def alive_players(self):
		return [player for player in self.players if player.alive]

	def set_lovers(self, first_lover, second_lover):
		self.lovers = (first_lover, second_lover)

	def get_lover(self, player):
		if not self.lovers or player not in self.lovers:
			return None

		first_lover, second_lover = self.lovers

		return second_lover if player is first_lover else first_lover

	def are_lovers(self, first_player, second_player):
		return self.get_lover(first_player) is second_player

	def kill_player(self, player):
		if player.alive:
			player.alive = False
			self.dead_this_night.append(player)

			game_lover = self.get_lover(player)

			if game_lover is not None and game_lover.alive:
				self.log(texts.LOVER_GRIEF.format(lover_id=game_lover.id, role_name=game_lover.role.__class__.__name__, dead_id=player.id))
				self.kill_player(game_lover)

	def resurrect_player(self, player):
		if player in self.dead_this_night:
			player.alive = True
			self.dead_this_night.remove(player)

			game_lover = self.get_lover(player)

			if game_lover is not None and game_lover in self.dead_this_night:
				self.resurrect_player(game_lover)
	
	def is_over(self):
		alive_players = self.alive_players()
		n_wolves = sum(player.role.camp == texts.WOLVES and player.alive for player in self.players)
		n_villagers = sum(player.role.camp == texts.VILLAGERS and player.alive for player in self.players)
		
		if len(alive_players) == 2 and self.are_lovers(alive_players[0], alive_players[1]):
			return True, texts.LOVERS
		elif n_wolves == 0:
			return True, texts.VILLAGERS
		elif n_villagers == 0:
			return True, texts.WOLVES
		else:
			return False, None
		
	def play(self):
		self.log(texts.GAME_START)
		
		# if USE_SHERIFF == 1:
		#	self.log(texts.SHERIFF_TURN)
		#	Sheriff.elect(self, get_most_convincing_candidates(self.alive_players()))
		# TODO: il faudra revoir la mécanique d'élection du maire

		while True:
			self.current_day += 1

			night_phase(self)
			day_phase(self)
   
			over, winner = self.is_over()
   
			if over:
				break

		self.log(f"\n{texts.GAME_OVER.format(winner=winner)}")

		return winner
