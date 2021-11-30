import lib.bughouse as bug # the bughouse board
import chess
import eval_constants
from zh_eng import ALL_PIECES

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


def evaluate_board(board, color):
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

def generate_legal_zh_moves(board):
	moves = list(board.legal_moves) # Get all the standard moves

	for sq in board.legal_drop_squares(): # All the legal squares that can receive a piece
		for piece in ALL_PIECES:
			if board.pockets[board.turn].count(piece) >= 1:
				moves.append(chess.Move(from_square=sq, to_square=sq, drop=piece)) # Add those as move options
	return moves

def generate_legal_bug_moves(board, player_num):
	assert board.in_sync() # Boards need to be in sync
	b1 = generate_legal_zh_moves(board.boards[0])
	b2 = generate_legal_zh_moves(board.boards[1])	

	return [(b1[i], b2[j]) for i in range(len(b1)) for j in range(len(b2))]

def best_move(board, depth):
	alpha = -1000000
	beta = 1000000
	tp_table = {} # We don't need to evaluate the same board twice.  Essentially memoization for a chess engine

	best_move = None
	best_move_score = -100000

	for move in generate_legal_bug_moves(board, 0):
		# print(move)
		new_board = board.deepcopy()

		board.push(move)
		nodes = {0:0}
		score = perform_tree_search_(board, depth, board.turn == chess.WHITE, alpha, beta, tp_table, nodes)
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
		board.pop()
		print(move, score, nodes[0])

	return (best_move, best_move_score)

# Performs AB minimax search given a depth, player, a, b, and transposition table
# Based on https://github.com/rselwyn/tactic-generator/blob/master/src/engine.cpp#L167
def perform_tree_search_(board, depth, isMaximizing, alpha, beta, tp_table, nodes_hit):
	nodes_hit[0] += 1
	if depth == 0:
		return evaluate_(board)

	if board.fen() in tp_table:
		return tp_table[board.fen()] # memoization

	if isMaximizing:
		bestValue = - LARGE_NUM
		possibleMoves = []
		for candidate_move in generate_legal_zh_moves(board):
			# print("pushing candidate", candidate_move)
			board.push(candidate_move)
			minimax_result = perform_tree_search_(board, depth - 1, not isMaximizing, alpha, beta, tp_table, nodes_hit)
			bestValue = max(bestValue, minimax_result)
			alpha = max(alpha, bestValue)
			board.pop()

			if alpha > beta:
				break

		tp_table[board.fen()] = bestValue
		return bestValue
	else:
		bestValue = LARGE_NUM
		possibleMoves = []
		for candidate_move in generate_legal_zh_moves(board):
			# print("pushing candidate", candidate_move)
			board.push(candidate_move)
			minimax_result = perform_tree_search_(board, depth - 1, not isMaximizing, alpha, beta, tp_table, nodes_hit)
			bestValue = min(bestValue, minimax_result)
			beta = min(beta, bestValue)
			board.pop()

			if beta < alpha:
				break

		tp_table[board.fen()] = bestValue
		return bestValue



def evaluate_(board):
	# We assume that the team is of White P1 Black P2 vs Black P1 White P2
	return evaluate_board(board.boards[0], chess.WHITE) + evaluate_board(board.boards[1], chess.BLACK) - \
			 evaluate_board(board.boards[0], chess.BLACK) - evaluate_board(board.boards[1], chess.WHITE)

board = bug.BughouseBoard()
board.move(0, chess.Move.from_uci("e2e4"))

assert board.in_sync()