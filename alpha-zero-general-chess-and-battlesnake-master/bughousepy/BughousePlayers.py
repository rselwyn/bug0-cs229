import chess
from chess.variant import CrazyhouseBoard
from .BughouseBoard import BughouseBoard
from .BughouseNNRepresentation import move_to_index, board_to_input
from bughousepy.tensorflow.NNet import NNetWrapper as BughouseTensorflowNNet
from utils import dotdict
from MCTS import MCTS
import pickle

import numpy as np

# code taken from https://github.com/namin/alpha-zero-general/tree/_chess

class RandomPlayer():
    def __init__(self, game):
        self.game = game

    def __call__(self, board):
        valids = self.game.getValidMoves(board, None)
        moves = np.argwhere(valids==1).squeeze(-1)
        return np.random.choice(moves)


CONSTANTS = {
	chess.PAWN: [0,   0,   0,   0,   0,   0,   0,   0,
    60,  60,  60,  60,  70,  60,  60,  60,
    40,  40,  40,  50,  60,  40,  40,  40,
    20,  20,  20,  40,  50,  20,  20,  20,
     5,   5,  15,  30,  40,  10,   5,   5,
     5,   5,  10,  20,  30,   5,   5,   5,
     5,   5,   5, -30, -30,   5,   5,   5,
     0,   0,   0,   0,   0,   0,   0,   0], 
	chess.KNIGHT: [-20, -10,  -10,  -10,  -10,  -10,  -10,  -20,
    -10,  -5,   -5,   -5,   -5,   -5,   -5,  -10,
    -10,  -5,   15,   15,   15,   15,   -5,  -10,
    -10,  -5,   15,   15,   15,   15,   -5,  -10,
    -10,  -5,   15,   15,   15,   15,   -5,  -10,
    -10,  -5,   10,   15,   15,   15,   -5,  -10,
    -10,  -5,   -5,   -5,   -5,   -5,   -5,  -10,
    -20,   0,  -10,  -10,  -10,  -10,    0,  -20],
	chess.BISHOP: [    -20,    0,    0,    0,    0,    0,    0,  -20,
    -15,    0,    0,    0,    0,    0,    0,  -15,
    -10,    0,    0,    5,    5,    0,    0,  -10,
    -10,   10,   10,   30,   30,   10,   10,  -10,
      5,    5,   10,   25,   25,   10,    5,    5,
      5,    5,    5,   10,   10,    5,    5,    5,
    -10,    5,    5,   10,   10,    5,    5,  -10,
    -20,  -10,  -10,  -10,  -10,  -10,  -10,  -20], 
	chess.ROOK: [    0,   0,   0,   0,   0,   0,   0,   0,
   15,  15,  15,  20,  20,  15,  15,  15,
    0,   0,   0,   0,   0,   0,   0,   0,
    0,   0,   0,   0,   0,   0,   0,   0,
    0,   0,   0,   0,   0,   0,   0,   0,
    0,   0,   0,   0,   0,   0,   0,   0,
    0,   0,   0,   0,   0,   0,   0,   0,
    0,   0,   0,  10,  10,  10,   0,   0], 
	chess.KING: [0,    0,     0,     0,    0,    0,    0,    0,
				0,    0,     0,     0,    0,    0,    0,    0,
				0,    0,     0,     0,    0,    0,    0,    0,
				0,    0,     0,    20,   20,    0,    0,    0,
				0,    0,     0,    20,   20,    0,    0,    0,
				0,    0,     0,     0,    0,    0,    0,    0,
				0,    0,     0,   -10,  -10,    0,    0,    0,
				0,    0,    20,   -10,  -10,    0,   20,    0], 
	chess.QUEEN: [-30,  -20,  -10,  -10,  -10,  -10,  -20,  -30,
			    -20,  -10,   -5,   -5,   -5,   -5,  -10,  -20,
			    -10,   -5,   10,   10,   10,   10,   -5,  -10,
			    -10,   -5,   10,   20,   20,   10,   -5,  -10,
			    -10,   -5,   10,   20,   20,   10,   -5,  -10,
			    -10,   -5,   -5,   -5,   -5,   -5,   -5,  -10,
			    -20,  -10,   -5,   -5,   -5,   -5,  -10,  -20,
			    -30,  -20,  -10,  -10,  -10,  -10,  -20,  -30]
}

ALL_PIECES = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.KING, chess.QUEEN]

piece_values = {
	chess.PAWN: 100,
	chess.KNIGHT: 310,
	chess.BISHOP: 320,
	chess.ROOK: 500,
	chess.QUEEN: 900,
	chess.KING: 100000
}

LARGE_NUM = 1000000

# By making the piece more value in the "bag," the piece implicitly doesn't have as high of an incentive to be dropped.
# intuition is that pawns/bishops
# droppable_scalar = {
# 	chess.PAWN: .5,
# 	chess.KNIGHT: .5,
# 	chess.BISHOP: .4,
# 	chess.ROOK: 1,
# 	chess.QUEEN: 1,
# 	chess.KING: 0 # included to make the code later not need a special case.
# }

def evaluate_board(board: CrazyhouseBoard, color):
    eval_score_curr_player = 100 # Total Eval Score for the current position.  Start at 100 just to ensure > 0

    if board.is_checkmate():
        return LARGE_NUM # For all intents and purposes +inf

    # Raw Material
    for piece in ALL_PIECES:
        for piece_instance in board.pieces(piece, color):
            white_equiv = (7 - piece_instance // 8, piece_instance % 8)
            white_equiv = white_equiv[0] * 8 + white_equiv[1]
            eval_score_curr_player += piece_values[piece] + CONSTANTS[piece][piece_instance if color == chess.BLACK else white_equiv]

    # Material Held in Pocket
	# for piece in ALL_PIECES:
	# 	# print(piece)
	# 	eval_score_curr_player += piece_values[piece] * droppable_scalar[piece] \
	# 	 * board.pockets[color].count(piece)

    return eval_score_curr_player

class MinimaxBughousePlayer():

    def __init__(self, depth):
        self.depth = depth

    def __call__(self, board: BughouseBoard):

        start_with_maximizing = board.turn == chess.WHITE
        
        alpha = -LARGE_NUM
        beta = LARGE_NUM
        tp_table = {} # We don't need to evaluate the same board twice.  Essentially memoization for a chess engine

        best_move = None
        best_move_score = -LARGE_NUM if start_with_maximizing else LARGE_NUM

        if board.get_active_board().turn == chess.BLACK:
            board = board.mirror()
        
        for move in board.get_active_board().legal_moves:

            new_board = board.copy()
            self.move_(new_board, move)

            score = self.perform_tree_search_(new_board, self.depth, not start_with_maximizing, alpha, beta, tp_table)

            if start_with_maximizing and score > best_move_score:
                best_move = move
                best_move_score = score
                alpha = max(alpha, best_move_score)

            elif not start_with_maximizing and score < best_move_score:
                best_move = move
                best_move_score = score
                beta = min(beta, best_move_score)
            
        return move_to_index[best_move.uci()]

    # Performs AB minimax search given a depth, player, a, b, and transposition table
    # Based on https://github.com/rselwyn/tactic-generator/blob/master/src/engine.cpp#L167
    def perform_tree_search_(self, board: BughouseBoard, depth, isMaximizing, alpha, beta, tp_table):
        
        if depth == 0:
            return self.evaluate_(board)

        # if board.pos_string() in tp_table:
        # 	return tp_table[board.pos_string()] # memoization

        if isMaximizing:
            bestValue = - LARGE_NUM
            for candidate_move in board.get_active_board().legal_moves:
                new_board = board.copy()
                self.move_(new_board, candidate_move)
                minimax_result = self.perform_tree_search_(new_board, depth - 1, not isMaximizing, alpha, beta, tp_table)
                bestValue = max(bestValue, minimax_result)
                alpha = max(alpha, bestValue)

                if alpha > beta:
                    break

            # tp_table[board.pos_string()] = bestValue
            return bestValue
        else:
            bestValue = LARGE_NUM
            for candidate_move in board.get_active_board().legal_moves:
                new_board = board.copy()
                self.move_(new_board, candidate_move)
                minimax_result = self.perform_tree_search_(new_board, depth - 1, not isMaximizing, alpha, beta, tp_table)
                bestValue = min(bestValue, minimax_result)
                beta = min(beta, bestValue)

                if beta < alpha:
                    break

            # tp_table[board.pos_string()] = bestValue
            return bestValue

    def move_(self, board: BughouseBoard, move):
        board.move(move)

    def evaluate_(self, board: BughouseBoard):
        # We assume that the team is of White P1 Black P2 vs Black P1 White P2
        return evaluate_board(board.boards[0], chess.WHITE) + evaluate_board(board.boards[1], chess.BLACK) - \
                evaluate_board(board.boards[0], chess.BLACK) - evaluate_board(board.boards[1], chess.WHITE)


class LazyMinimaxBughousePlayer(MinimaxBughousePlayer):

    def move_(self, board: BughouseBoard, move):
        active_board = board.active_board
        board.move(move)
        board.active_board = active_board

    def evaluate_(self, board: BughouseBoard):
        return evaluate_board(board.get_active_board(), board.active_board^chess.WHITE) - evaluate_board(board.get_active_board(), board.active_board^chess.BLACK)


class NNBughousePlayer():

    def __init__(self, game, numMCTSSims, cpuct=1.0, nnet=BughouseTensorflowNNet, folder='temp', filename=None):

        self.game = game
        self.nnet = nnet(self.game)

        if filename is not None:
            self.nnet.load_checkpoint(folder=folder, filename=filename)
            print(f"Loaded checkpoint {filename}")

        self.args = dotdict({'numMCTSSims': numMCTSSims, 'cpuct': cpuct})
        self.mcts = MCTS(game, self.nnet, self.args)

    def __call__(self, board):
        return np.argmax(self.mcts.getActionProb(board, temp=0))

    def callback(self):
        self.mcts = MCTS(self.game, self.nnet, self.args)


class SupervisedPlayer():

    def __init__(self, filename):
        with open(filename, 'rb') as f:
            self.model = pickle.load(f)

    def __call__(self, board: BughouseBoard):

        start_with_maximizing = board.turn == chess.WHITE
        
        alpha = -LARGE_NUM
        beta = LARGE_NUM
        tp_table = {} # We don't need to evaluate the same board twice.  Essentially memoization for a chess engine

        best_move = None
        best_move_score = -LARGE_NUM if start_with_maximizing else LARGE_NUM

        if board.get_active_board().turn == chess.BLACK:
            board = board.mirror()
        
        possible_boards = []
        for move in board.get_active_board().legal_moves:

            new_board = board.copy()
            self.move_(new_board, move)
            
            possible_boards.append(board_to_input(new_board).flatten())
        
        possible_boards = np.stack(possible_boards).astype(np.int8)
        scores = self.model.predict(possible_boards)
        
        best_move_index = np.amax(scores, axis=0)
        best_move = board.get_active_board().legal_moves()[best_move_index]
            
        return move_to_index[best_move.uci()]

    def move_(self, board: BughouseBoard, move):
        board.move(move)
