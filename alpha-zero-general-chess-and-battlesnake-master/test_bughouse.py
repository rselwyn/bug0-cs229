import Arena
from utils import *

from bughousepy.BughouseGame import BughouseGame
from bughousepy.BughousePlayers import RandomPlayer, MinimaxBughousePlayer, LazyMinimaxBughousePlayer, NNBughousePlayer

import numpy as np
# np.random.seed(0)

import cProfile, pstats
pr = cProfile.Profile()

def profile(f):

    pr.enable()
    f()
    pr.disable()
    stats = pstats.Stats(pr).strip_dirs().sort_stats('cumtime')
    stats.print_stats(30)

game = BughouseGame()

rp = RandomPlayer(game=game)
eng = LazyMinimaxBughousePlayer(depth=1)
n1p = NNBughousePlayer(game=game, numMCTSSims=5, filename='checkpoint_1.pth.tar')

# arena = Arena.Arena(n1p, rp, game, display=lambda board: game.display(board, visualize=False, string_rep=True, result=True))

# print(arena.playGames(100, verbose=False, switch=True))

arena = Arena.Arena(rp, n1p, game, display=lambda board: game.display(board, visualize=False, string_rep=False, result=False))

print(arena.playGames(100, verbose=True, switch=False))

# print(arena.playGames(100, verbose=False, switch=False, invert=True))

# profile(lambda: print(arena.playGames(10, verbose=False, switch=False)))