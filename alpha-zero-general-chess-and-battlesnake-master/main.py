import sys
import threading

from Coach import Coach
from crazyhousepy.CrazyhouseGame import CrazyhouseGame as Game
from crazyhousepy.pytorch.NNet import NNetWrapper as nn
from utils import *


args = dotdict({
    'numIters': 100,
    'numEps': 10,              # Number of complete self-play games to simulate during a new iteration.
    'tempThreshold': 15,        #
    'updateThreshold': 0.6,     # During arena playoff, new neural net will be accepted if threshold or more of games are won.
    'maxlenOfQueue': 200000,    # Number of game examples to train the neural networks.
    'numMCTSSims': 10,          # Number of games moves for MCTS to simulate.
    'arenaCompare': 40,         # Number of games to play during arena play to determine if new net will be accepted.
    'cpuct': 1,

    'checkpoint': './training/',
    'load_model': False,
    'load_folder_file': ('./training/model/','best.pth.tar'),
    'numItersForTrainExamplesHistory': 20,

})

if __name__ == "__main__":
    my_game = Game()
    nnet = nn(my_game)

    if args.load_model:
        nnet.load_checkpoint(args.load_folder_file[0], args.load_folder_file[1])

    c = Coach(my_game, nnet, args)
    if args.load_model:
        print("Load trainExamples from file")
        c.loadTrainExamples()
    sys.setrecursionlimit(100000)
    threading.stack_size(200000000)
    thread = threading.Thread(target=c.learn())
    thread.start()
    # c.learn()
