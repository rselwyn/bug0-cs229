# from bughousepy.BughouseGame import create_uci_labels

# labels = create_uci_labels()

# print(len(labels))

from random import Random
import chess
from chess.variant import CrazyhouseBoard
from chess_utils.utils import bitboard_to_array

from bughousepy.BughouseGame import BughouseGame, libPlayerToBughousePlayer
# from bughousepy.pytorch.NNet import NNetWrapper as BughousePytorchNNet
# from bughousepy.tensorflow.NNet import NNetWrapper as BughouseTensorflowNNet
from bughousepy.bug_lazy_eng import best_move, evaluate_board
from bughousepy.BughouseNNRepresentation import move_to_index
from bughousepy.BughouseBoard import BughouseBoard

from bughousepy.BughousePlayers import RandomPlayer, MinimaxBughousePlayer, LazyMinimaxBughousePlayer

# import torchinfo

import Arena
from MCTS import MCTS

from utils import *

import numpy as np
# np.random.seed(0)

import timeit
import cProfile, pstats
pr = cProfile.Profile()
def profile(f):

    pr.enable()
    f()
    pr.disable()
    stats = pstats.Stats(pr).strip_dirs().sort_stats('cumtime')
    stats.print_stats(30)

# board = CrazyhouseBoard()
# # board.push(chess.Move(chess.E2, chess.E4))
# # board.push(chess.Move(chess.E7, chess.E5))

# # board.push(chess.Move(chess.B8, chess.C6))

# print(board)

# evaluate_board(board, chess.WHITE)
# evaluate_board(board, chess.BLACK)

# exit()

game = BughouseGame()

# Random vs random
# rp = lambda board : np.random.choice(np.argwhere(game.getValidMoves(board, libPlayerToBughousePlayer(board.turn))==1).squeeze(-1))
# eng = lambda board : move_to_index[best_move(board, 3)[0].uci()]

rp = RandomPlayer(game=game).play
eng = LazyMinimaxBughousePlayer(depth=1).play

def test_rp(board):

    print("---")
    print("FIRST_BOARD, WHITE:", evaluate_board(board.first_board, chess.WHITE))
    print("FIRST_BOARD, BLACK:", evaluate_board(board.first_board, chess.BLACK))
    # mirror = board.first_board.mirror()
    # print("FIRST_BOARD_MIRROR, WHITE:", evaluate_board(mirror, chess.WHITE))
    # print("FIRST_BOARD_MIRROR, BLACK:", evaluate_board(mirror, chess.BLACK))

    print("SECOND_BOARD, WHITE:", evaluate_board(board.second_board, chess.WHITE))
    print("SECOND_BOARD, BLACK:", evaluate_board(board.second_board, chess.BLACK))
    # mirror = board.second_board.mirror()
    # print("SECOND_BOARD_MIRROR, WHITE:", evaluate_board(mirror, chess.WHITE))
    # print("SECOND_BOARD_MIRROR, BLACK:", evaluate_board(mirror, chess.BLACK))

    print("---")

    return rp(board)

arena = Arena.Arena(eng, rp, game, display=lambda board: game.display(board, visualize=False, string_rep=True, result=True))
# print(arena.playGames(100, verbose=False, switch=False))
print(arena.playGames(1, verbose=True, switch=False, invert=False))
# profile(lambda: print(arena.playGames(10, verbose=False, switch=False)))

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