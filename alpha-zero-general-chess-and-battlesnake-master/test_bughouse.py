import Arena
from MCTS import MCTS
from utils import *

from bughousepy.BughouseGame import BughouseGame
from bughousepy.BughousePlayers import RandomPlayer, MinimaxBughousePlayer, LazyMinimaxBughousePlayer

from bughousepy.tensorflow.NNet import NNetWrapper as BughouseTensorflowNNet

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

rp = RandomPlayer(game=game).play
eng = LazyMinimaxBughousePlayer(depth=1).play

# args = dotdict({'numMCTSSims': 5, 'cpuct': 1.0})
# nnet = BughouseTensorflowNNet(game)
# nnet.load_checkpoint(folder='temp', filename='checkpoint_16.pth.tar')
# mcts = MCTS(game, nnet, args)
# n1p = lambda x: np.argmax(mcts.getActionProb(x, temp=0))

arena = Arena.Arena(eng, rp, game, display=lambda board: game.display(board, visualize=False, string_rep=True, result=True))

print(arena.playGames(100, verbose=False, switch=False))
print(arena.playGames(100, verbose=False, switch=False, invert=True))

# profile(lambda: print(arena.playGames(10, verbose=False, switch=False)))