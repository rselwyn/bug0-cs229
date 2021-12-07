import logging
from math import e
import os
import sys
from collections import deque
from pickle import Pickler, Unpickler
from random import shuffle

import numpy as np
from tqdm import tqdm

from Arena import Arena
from MCTS import MCTS

from utils import dotdict

sys.path.append("..")
sys.path.append("../q_learning/")
from q_learning.process_data import load_data_from_text, clean_moves
from bughousepy.BughouseNNRepresentation import move_to_index, num_possible_moves, board_to_input, all_possible_moves
from bughousepy.BughouseBoard import BughouseBoard
from bughousepy.BughouseGame import BughouseGame
from bughousepy.tensorflow.NNet import NNetWrapper as BughouseTensorflowNNet
import time
import re

import chess
from chess_utils.utils import swap_uci_label

import traceback

log = logging.getLogger(__name__)

class SupervisedCoach():
    """
    This class executes the self-play + learning. It uses the functions defined
    in Game and NeuralNet. args are specified in main.py.
    """

    def __init__(self, game, nnet, args):
        self.game = game
        self.nnet = nnet
        self.args = args
        self.trainExamples = []

    def learn(self):

        i = 1
        while i <= self.args.num_files:
            
            self.trainExamples = []
            j = 0
            while j < self.args.num_files_together and i <= self.args.num_files:
                print(f"Loading example file {i+j}")
                self.trainExamples += self.loadTrainExamples(i+j)
                i+=1
                j+=1
            
            self.nnet.train(self.trainExamples)
        
            self.nnet.save_checkpoint(folder=self.args.checkpoint, filename=self.getCheckpointFile(i-1))
            self.nnet.save_checkpoint(folder=self.args.checkpoint, filename='best.pth.tar')

    def getCheckpointFile(self, iteration):
        return 'checkpoint_' + str(iteration) + '.pth.tar'

    def loadTrainExamples(self,iteration):
        modelFile = os.path.join(self.args.load_folder_file[0], f"checkpoint_{iteration}_"+self.args.load_folder_file[1])
        examplesFile = modelFile + ".examples"
        
        with open(examplesFile, "rb") as f:
            log.info("File with trainExamples found. Loading it...")
            trainExamples = Unpickler(f).load()
        log.info('Loading done!')

        return trainExamples

def generate_boards_fens_moves(moves):

    # move_string = moves
    moves = list(filter(None, moves.split(" ")))    

    # if not all(x[-1] == "}" for x in moves[1::2]):
    #     print(move_string)
    #     print(list(x for x in moves[1::2] if x[-1] != "}"))
    #     print()

    if len(moves) < 8:
        print("Early forfeit")
        return None, None, None
    
    if len(moves) / 2 % 1 != 0:
        print(len(moves), '\n'.join(moves))
        return None, None, None

    boards = []
    fens = []
    labels = []

    board = BughouseBoard()

    for i in range(len(moves) // 2):

        if len(moves[2*i]) < 3:
            return None, None, None
        board_num = int(moves[2*i][-2].lower() == 'b')
        board.active_board = board_num

        boards.append(board)
        fens.append(board.string_rep())

        board = board.copy()

        # team = int(moves[2*i][-2].isupper())
        move = moves[2*i+1]
        assert len(move) != 3, print(move)
        # print(move)
        timing = re.search(r"{(.*?)}", move)
        if timing is None:
            print(move, moves)
            assert False
        move = move.replace(timing.group(0), "")
        try:
            move = board.parse_san(board_num, move)
            labels.append(move_to_index[swap_uci_label(move.uci()) if board.get_active_board().turn == chess.BLACK else move.uci()])
            board.move(move, board_num)
        except Exception as e:
            print(' '.join(moves))
            print(moves[2*i+1])
            traceback.print_exc()
            return None, None, None
        

    return boards, fens, labels


def build_state_value_dataset(folder, file, checkpoint_freq=1000, print_freq=100):

    print("Loading data")

    filename = os.path.join(folder, f"{file}.moves")

    if not os.path.exists(filename):

        filename = os.path.join(folder, f"{file}.bpgn")
        with open(filename, "r", encoding="utf-8", errors="replace") as f:

            games_moves = load_data_from_text(f.read())

            out = []

            for moves in games_moves:
                if moves[-1] == '*':
                    continue
                moves = re.sub(r'\uFFFD', '', moves)
                moves_string = moves.replace(re.search(r'{(?:.(?!{))+$', moves).group(0), "").strip()
                moves_string = re.sub(r"{C:(.*?)}", '', moves_string)
                moves_string = moves_string.replace("{C:}", "")
                out.append((moves[-3:], moves_string))

            games_moves = out

        filename = os.path.join(folder, f"{file}.moves")
        with open(filename, "wb") as f:
            Pickler(f).dump(games_moves)

    else:
        with open(filename, "rb") as f:
            games_moves = Unpickler(f).load()

    print("Building dataset")

    examples = []
    times = []

    c = 1

    for i, (result, moves_string) in enumerate(games_moves):

        t = time.time()
        
        try:

            result = 1 if result == "1-0" else -1 if result == "0-1" else 0 if result == "1/2" else None

            # if result is None:
            #     print("result is None!")

            boards, fens, moves = generate_boards_fens_moves(moves_string)

            if boards is None or fens is None or moves is None:
                print(f"Error on i={i}")
                continue
            
            # print(moves_string)
            # print([all_possible_moves[m] for m in moves])
            
            # for f in fens:
            #     print(f)
            # print(result)
            
            final_move = chess.Move.from_uci(all_possible_moves[moves[-1]])
            if boards[-1].get_active_board().turn == chess.BLACK:
                final_board = boards[-1].mirror()
                final_board.move(final_move)
                final_board = final_board.mirror()
            else:
                final_board = boards[-1].copy()
                final_board.move(final_move)

            r = final_board.result()
            if r != "*":
                r = 1 if r == "1-0" else -1 if r == "0-1" else 0 if r == "1/2" else None
                if r != result:
                    print(moves_string)
                    print(final_board.first_board.result(), final_board.second_board.result())
                    print(f"Results not equal on i={i}, expected {result} but played to {r}")

            # print(final_board.result())

            # if len(boards) != len(fens) or len(fens) != len(moves):
            #     print(len(boards), len(fens), len(moves))
            #     assert False
            for b, m in zip(boards, moves):
                p = np.zeros((num_possible_moves,))
                p[m] = 1
                examples.append((b, p, result*(1 if b.turn else -1)))
        
        except Exception:
            print(moves_string)
            traceback.print_exc()
            print(f"Error on i={i}")
            continue
        
        if i % checkpoint_freq == checkpoint_freq-1:
            print(f"Dumping checkpoint #{c}")
            filename = os.path.join(folder, f"checkpoint_{c}_{file}.examples")
            with open(filename, "wb") as f:
                Pickler(f).dump(examples)
            examples = []
            c += 1
        
        times.append(time.time() - t)
        
        if i % print_freq == print_freq-1:
            print(i, f"{(i+1) / len(games_moves) * 100}% complete")
            print(f"Time taken: {np.sum(times)}, average time per game: {np.mean(times)} estimated time left: {(len(games_moves) - i + 1) * np.mean(times)}, estimated total time: {len(games_moves) * np.mean(times)}")


    filename = os.path.join(folder, f"checkpoint_{c}_{file}.examples")
    with open(filename, "wb") as f:
        Pickler(f).dump(examples)

    return examples

if __name__ == '__main__':
    DATA_DIR = "./bughouse_data/"
    # filenames = [f"export{i}" for i in range(2005, 2020)][::-1]
    # filenames = ["export2019"]
    # for filename in filenames:
    #     print(f"Processing {filename}")
    #     build_state_value_dataset(DATA_DIR, filename)

    args = dotdict({
        'checkpoint': './temp/',
        'load_folder_file': (DATA_DIR,'export2019'),
        'num_files': 7,
        'num_files_together': 1,
    })

    g = BughouseGame()
    nnet = BughouseTensorflowNNet(g)

    c = SupervisedCoach(g, nnet, args)

    log.info('Starting the learning process 🎉')
    c.learn()