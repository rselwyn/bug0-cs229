# from bughousepy.BughouseGame import create_uci_labels

# labels = create_uci_labels()

# print(len(labels))
from othello.OthelloPlayers import *
from bughousepy.BughouseGame import BughouseGame
import Arena
import numpy as np
np.random.seed(0)

import cProfile, pstats

pr = cProfile.Profile()

game = BughouseGame()

rp = RandomPlayer(game).play
arena = Arena.Arena(rp, rp, game, display=game.display)

pr.enable()
print(arena.playGames(4, verbose=False))
pr.disable()

stats = pstats.Stats(pr).strip_dirs().sort_stats('cumtime')
stats.print_stats(30)
