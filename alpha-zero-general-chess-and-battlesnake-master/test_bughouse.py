# from bughousepy.BughouseGame import create_uci_labels

# labels = create_uci_labels()

# print(len(labels))

from bughousepy.BughouseGame import BughouseGame, libPlayerToBughousePlayer
# from bughousepy.pytorch.NNet import NNetWrapper as BughousePytorchNNet
# from bughousepy.tensorflow.NNet import NNetWrapper as BughouseTensorflowNNet
from bughousepy.bug_eng import best_move
from bughousepy.BughouseNNRepresentation import move_to_index

# import torchinfo

import Arena
from MCTS import MCTS

from utils import *

import numpy as np
np.random.seed(0)

import timeit
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
rp = lambda board : np.random.choice(np.argwhere(game.getValidMoves(board, libPlayerToBughousePlayer(board.turn))==1).squeeze(-1))
eng = lambda board : move_to_index[best_move(board, 2)[0].uci()]

arena = Arena.Arena(rp, eng, game, display=lambda board: game.display(board, visualize=False, string_rep=True, result=True))
print(arena.playGames(100, verbose=False))
# profile(lambda: print(arena.playGames(100, verbose=False)))

# Random vs random-init NN
# args = dotdict({'numMCTSSims': 5, 'cpuct': 1.0})
# nnet = BughouseTensorflowNNet(game)
# nnet.load_checkpoint(folder='temp', filename='checkpoint_16.pth.tar')
# mcts = MCTS(game, nnet, args)
# n1p = lambda x: np.argmax(mcts.getActionProb(x, temp=0))

# arena = Arena.Arena(n1p, rp, game, display=lambda board: game.display(board, visualize=False, string_rep=True))
# profile(lambda: print(arena.playGames(100, verbose=False)))

# board = game.toArray(game.getInitBoard())  
# print(timeit.timeit(lambda: nnet.predict(board),number=10))

# torchinfo.summary(nnet.nnet, input_size=(64, 60, 8, 8))