# from bughousepy.BughouseGame import create_uci_labels

# labels = create_uci_labels()

# print(len(labels))

from othello.OthelloPlayers import *
from bughousepy.BughouseGame import BughouseGame
from bughousepy.pytorch.NNet import NNetWrapper as BughousePytorchNNet

import Arena
from MCTS import MCTS

from utils import *

import numpy as np
np.random.seed(0)

import cProfile, pstats
pr = cProfile.Profile()
def profile(f):

    pr.enable()
    f()
    pr.disable()
    stats = pstats.Stats(pr).strip_dirs().sort_stats('cumtime')
    stats.print_stats(30)

game = BughouseGame()

# Random vs random
rp = RandomPlayer(game).play

# arena = Arena.Arena(rp, rp, game, display=lambda board: game.display(board, visualize=False, string_rep=True))
# profile(lambda: print(arena.playGames(4, verbose=False)))

# Random vs random-init NN
args = dotdict({'numMCTSSims': 2, 'cpuct': 1.0})
mcts = MCTS(game, BughousePytorchNNet(game), args)
n1p = lambda x: np.argmax(mcts.getActionProb(x, temp=0))

arena = Arena.Arena(n1p, rp, game, display=lambda board: game.display(board, visualize=False, string_rep=True))
profile(lambda: print(arena.playGames(2, verbose=False)))