import random

from chess import Move

from deepChess.Agent import Agent
from deepChess.ChessUtils import MyChessEnv


class RandomBot(Agent):
    def select_move(self, env: MyChessEnv):
        """Choose a random valid move that preserves our own eyes."""
        randommove = random.choice(env.possible_moves())
        # if not candidates:
        #     return Move.pass_turn()
        return randommove
