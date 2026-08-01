from roles.base import Role
from game import texts

class Sheriff(Role):
    vote_weight = 2

    @classmethod
    def choose_candidate_for_voter(cls, game, voter, candidates):
        suspicion_scores = game.suspicion.get_suspicion_scores(voter.id)
        lowest_suspicion = min(suspicion_scores[candidate.id] for candidate in candidates)
        least_suspicious_candidates = [candidate for candidate in candidates if suspicion_scores[candidate.id] == lowest_suspicion]

        return game.rng.choice(least_suspicious_candidates)

    @classmethod
    def elect(cls, game, candidates):
        candidates = candidates or game.alive_players()
        vote_counts = {}

        for voter in game.alive_players():
            vote = cls.choose_candidate_for_voter(game, voter, candidates)
            vote_counts[vote.id] = vote_counts.get(vote.id, 0) + 1

        max_votes = max(vote_counts.values())
        tied_candidate_ids = [candidate_id for candidate_id, votes in vote_counts.items() if votes == max_votes]
        sheriff_id = game.rng.choice(tied_candidate_ids)

        game.sheriff = game.players[sheriff_id]
        game.sheriff.vote_weight = cls.vote_weight

        game.log(texts.SHERIFF_ELECTED.format(sheriff_id=sheriff_id))

    @classmethod
    def appoint_successor(cls, game, candidates):
        game.sheriff.vote_weight = 1

        if not candidates:
            game.sheriff = None
            return

        successor = cls.choose_candidate_for_voter(game, game.sheriff, candidates)
        game.sheriff = successor
        game.sheriff.vote_weight = cls.vote_weight

        game.log(texts.SHERIFF_SUCCESSOR.format(player_id=successor.id))
