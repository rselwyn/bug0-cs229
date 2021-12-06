import chess
from . import eval_constants

from chess.variant import CrazyhouseBoard
from .BughouseBoard import BughouseBoard

from chess_utils.utils import bitboards_to_array

import numpy as np

ALL_PIECES = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.KING, chess.QUEEN]

piece_values = {
	chess.PAWN: 100,
	chess.KNIGHT: 310,
	chess.BISHOP: 320,
	chess.ROOK: 500,
	chess.QUEEN: 900,
	chess.KING: 100000
}

# print(np.array([np.array(eval_constants.CONSTANTS[piece]) for piece in ALL_PIECES]).reshape((-1,8,8)))
# CONSTANTS_NDARRAY = np.array([piece_values[piece] + np.array(eval_constants.CONSTANTS[piece]) for piece in ALL_PIECES]).reshape((-1,8,8))
# print(CONSTANTS_NDARRAY.dtype)

LARGE_NUM = 100000

# By making the piece more value in the "bag," the piece implicitly doesn't have as high of an incentive to be dropped.
# intuition is that pawns/bishops
droppable_scalar = {
	chess.PAWN: .5,
	chess.KNIGHT: .5,
	chess.BISHOP: .4,
	chess.ROOK: 1,
	chess.QUEEN: 1,
	chess.KING: 0 # included to make the code later not need a special case.
}


def evaluate_board(board: CrazyhouseBoard, color):
	eval_score_curr_player = 100 # Total Eval Score for the current position.  Start at 100 just to ensure > 0

	if board.is_checkmate():
		return 1000000 # For all intents and purposes +inf

	# Raw Material
	for piece in ALL_PIECES:
		# print(chess.piece_name(piece), int(board.pieces(piece, color)))
		for piece_instance in board.pieces(piece, color):
			# print(chess.piece_name(piece), piece_instance)
			white_equiv = (7 - piece_instance // 8, piece_instance % 8)
			white_equiv = white_equiv[0] * 8 + white_equiv[1]
			eval_score_curr_player += piece_values[piece] + eval_constants.CONSTANTS[piece][piece_instance if color == chess.BLACK else white_equiv]

	# color_mask = board.occupied_co[color]

	# bitboards = np.array([
	# 	color_mask & board.pawns,
	# 	color_mask & board.knights,
	# 	color_mask & board.bishops,
	# 	color_mask & board.rooks,
    #     color_mask & board.kings,
    #     color_mask & board.queens,
    # ], dtype=np.uint64)

	# if color == chess.BLACK:
	# 	bitboards = chess.flip_vertical(bitboards)
	
	# bitboards = bitboards_to_array(bitboards)

	# eval_score_curr_player += np.sum(CONSTANTS_NDARRAY*bitboards)

	# print(bitboards)

	# print("WHITE" if color == chess.WHITE else "BLACK")
	# print(bitboards[0])

	# print("WHITE" if color == chess.WHITE else "BLACK", np.sum(CONSTANTS_NDARRAY*bitboards)+100, eval_score_curr_player)

	# Material Held in Pocket
	# for piece in ALL_PIECES:
	# 	# print(piece)
	# 	eval_score_curr_player += piece_values[piece] * droppable_scalar[piece] \
	# 	 * board.pockets[color].count(piece)

	return eval_score_curr_player


def best_move(board: BughouseBoard, depth):

	start_with_maximizing = board.turn == chess.WHITE
	
	alpha = -1000000
	beta = 1000000
	tp_table = {} # We don't need to evaluate the same board twice.  Essentially memoization for a chess engine

	best_move = None
	best_move_score = -100000 if start_with_maximizing else 100000

	# print("...")
	# print("P1" if board.turn == chess.WHITE else "P2")
	# print("FIRST_BOARD" if board.active_board == 0 else "SECOND_BOARD")
	# print("WHITE" if board.get_active_board().turn == chess.WHITE else "BLACK")
	# print("---")

	if board.get_active_board().turn == chess.BLACK:
		board = board.mirror()
	
	# print("P1" if board.turn == chess.WHITE else "P2")
	# print("FIRST_BOARD" if board.active_board == 0 else "SECOND_BOARD")
	# print("WHITE" if board.get_active_board().turn == chess.WHITE else "BLACK")
	# print("...")

	nodes = {0:0}

	for move in board.get_active_board().legal_moves:
		# print(move)

		new_board = board.copy()
		active_board = new_board.active_board
		new_board.move(move)
		new_board.active_board = active_board

		score = perform_tree_search_(new_board, depth, not start_with_maximizing, alpha, beta, tp_table, nodes)
		"""
					// Update Alpha and Beta
			if (!b->sideToMove) {
				alpha = std::max(alpha, extreme_value[index]);
			}
			else {
				beta = std::min(beta, extreme_value[index]);
			}"""

		if start_with_maximizing and score > best_move_score:
			best_move = move
			best_move_score = score
			alpha = max(alpha, best_move_score)

		elif not start_with_maximizing and score < best_move_score:
			best_move = move
			best_move_score = score
			beta = min(beta, best_move_score)
		
		# print(move, score, nodes[0])

	# print(best_move, best_move_score, nodes[0])
	return (best_move, best_move_score)

# Performs AB minimax search given a depth, player, a, b, and transposition table
# Based on https://github.com/rselwyn/tactic-generator/blob/master/src/engine.cpp#L167
def perform_tree_search_(board: BughouseBoard, depth, isMaximizing, alpha, beta, tp_table, nodes_hit):
	nodes_hit[0] += 1
	# print(f"DEPTH [{depth}]", "P1" if board.turn == chess.WHITE else "P2", "FIRST" if board.active_board == 0 else "SECOND")
	if depth == 0:
		return evaluate_(board)

	# if board.pos_string() in tp_table:
	# 	return tp_table[board.pos_string()] # memoization

	if isMaximizing:
		bestValue = - LARGE_NUM
		possibleMoves = []
		for candidate_move in board.get_active_board().legal_moves:
			# print("pushing candidate", candidate_move)
			new_board = board.copy()
			active_board = new_board.active_board
			new_board.move(candidate_move)
			new_board.active_board = active_board
			minimax_result = perform_tree_search_(new_board, depth - 1, not isMaximizing, alpha, beta, tp_table, nodes_hit)
			bestValue = max(bestValue, minimax_result)
			alpha = max(alpha, bestValue)

			if alpha > beta:
				break

		# tp_table[board.pos_string()] = bestValue
		return bestValue
	else:
		bestValue = LARGE_NUM
		possibleMoves = []
		for candidate_move in board.get_active_board().legal_moves:
			# print("pushing candidate", candidate_move)
			new_board = board.copy()
			active_board = new_board.active_board
			new_board.move(candidate_move)
			new_board.active_board = active_board
			minimax_result = perform_tree_search_(new_board, depth - 1, not isMaximizing, alpha, beta, tp_table, nodes_hit)
			bestValue = min(bestValue, minimax_result)
			beta = min(beta, bestValue)

			if beta < alpha:
				break

		# tp_table[board.pos_string()] = bestValue
		return bestValue


def evaluate_(board: BughouseBoard):
	# We assume that the team is of White P1 Black P2 vs Black P1 White P2
	return evaluate_board(board.get_active_board(), board.active_board^chess.WHITE) - evaluate_board(board.get_active_board(), board.active_board^chess.BLACK)
	# return evaluate_board(board.boards[0], chess.WHITE) + evaluate_board(board.boards[1], chess.BLACK) - \
	# 		 evaluate_board(board.boards[0], chess.BLACK) - evaluate_board(board.boards[1], chess.WHITE)