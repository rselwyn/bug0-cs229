import chess
from . import eval_constants

from chess.variant import CrazyhouseBoard
from .BughouseBoard import BughouseBoard

ALL_PIECES = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.KING, chess.QUEEN]

piece_values = {
	chess.PAWN: 1,
	chess.KNIGHT: 3,
	chess.BISHOP: 3.5,
	chess.ROOK: 5,
	chess.QUEEN: 9,
	chess.KING: 1000
}

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
		for piece_instance in board.pieces(piece, color):
			black_equiv = (7 - piece_instance // 8, piece_instance % 8)
			black_equiv = black_equiv[0] * 8 + black_equiv[1]
			eval_score_curr_player += piece_values[piece] + eval_constants.CONSTANTS[piece][piece_instance if color == chess.WHITE else black_equiv]

	# Material Held in Pocket
	for piece in ALL_PIECES:
		# print(piece)
		eval_score_curr_player += piece_values[piece] * droppable_scalar[piece] \
		 * board.pockets[color].count(piece)

	return eval_score_curr_player


def best_move(board: BughouseBoard, depth):
	alpha = -1000000
	beta = 1000000
	tp_table = {} # We don't need to evaluate the same board twice.  Essentially memoization for a chess engine

	best_move = None
	best_move_score = -100000

	if board.get_active_board().turn == chess.BLACK:
		board = board.mirror()

	for move in board.get_active_board().legal_moves:
		# print(move)

		new_board = board.copy()
		new_board.move(move)

		nodes = {0:0}
		score = perform_tree_search_(new_board, depth, board.turn == chess.WHITE, alpha, beta, tp_table, nodes)
		"""
					// Update Alpha and Beta
			if (!b->sideToMove) {
				alpha = std::max(alpha, extreme_value[index]);
			}
			else {
				beta = std::min(beta, extreme_value[index]);
			}"""

		if score > best_move_score:
			best_move = move
			best_move_score = score
			alpha = max(alpha, best_move_score)
		
		# print(move, score, nodes[0])

	return (best_move, best_move_score)

# Performs AB minimax search given a depth, player, a, b, and transposition table
# Based on https://github.com/rselwyn/tactic-generator/blob/master/src/engine.cpp#L167
def perform_tree_search_(board: BughouseBoard, depth, isMaximizing, alpha, beta, tp_table, nodes_hit):
	nodes_hit[0] += 1
	if depth == 0:
		return evaluate_(board)

	if board.string_rep() in tp_table:
		return tp_table[board.string_rep()] # memoization

	if isMaximizing:
		bestValue = - LARGE_NUM
		possibleMoves = []
		for candidate_move in board.get_active_board().legal_moves:
			# print("pushing candidate", candidate_move)
			new_board = board.copy()
			new_board.move(candidate_move)
			minimax_result = perform_tree_search_(new_board, depth - 1, not isMaximizing, alpha, beta, tp_table, nodes_hit)
			bestValue = max(bestValue, minimax_result)
			alpha = max(alpha, bestValue)

			if alpha > beta:
				break

		tp_table[board.string_rep()] = bestValue
		return bestValue
	else:
		bestValue = LARGE_NUM
		possibleMoves = []
		for candidate_move in board.get_active_board().legal_moves:
			# print("pushing candidate", candidate_move)
			new_board = board.copy()
			new_board.move(candidate_move)
			minimax_result = perform_tree_search_(new_board, depth - 1, not isMaximizing, alpha, beta, tp_table, nodes_hit)
			bestValue = min(bestValue, minimax_result)
			beta = min(beta, bestValue)

			if beta < alpha:
				break

		tp_table[board.string_rep()] = bestValue
		return bestValue



def evaluate_(board: BughouseBoard):
	# We assume that the team is of White P1 Black P2 vs Black P1 White P2
	return evaluate_board(board.boards[0], chess.WHITE) + evaluate_board(board.boards[1], chess.BLACK) - \
			 evaluate_board(board.boards[0], chess.BLACK) - evaluate_board(board.boards[1], chess.WHITE)
