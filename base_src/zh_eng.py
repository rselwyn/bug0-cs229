import chess.variant

def find_best_move(board):
	pass

piece_values = {
	chess.PAWN: 1,
	chess.KNIGHT: 3,
	chess.BISHOP: 3.5,
	chess.ROOK: 5,
	chess.QUEEN: 9,
	chess.KING: 1000
}

LARGE_NUM = 100000

DESIRED_DEPTH = 7 # ?

# By making the piece more value in the "bag," the piece implicitly doesn't have as high of an incentive to be dropped.
# intuition is that pawns/bishops
droppable_scalar = {
	chess.PAWN: .5,
	chess.KNIGHT: .5,
	chess.BISHOP: .4,
	chess.ROOK: 1,
	chess.QUEEN: 1,
}


ALL_PIECES = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.KING, chess.QUEEN]

def evaluate_board(board, color):
	eval_score_curr_player = 100 # Total Eval Score for the current position.  Start at 100 just to ensure > 0

	if board.is_checkmate():
		return 1000000 # For all intents and purposes +inf

	# Raw Material
	for piece in ALL_PIECES:
		for piece_instance in board.pieces(piece, color):
			eval_score_curr_player += piece_values[piece]

	# Material Held in Pocket
	for droppable_piece in board.pockets[color]: # All the droppable pieces for the current player
		eval_score_curr_player += piece_values[droppable_piece] * droppable_scalar[droppable_piece]

	return eval_score_curr_player

def evaluate_(board):
	if board.turn == chess.BLACK:
		return evaluate_board(board, chess.BLACK) - evaluate_board(board, chess.WHITE)
	return evaluate_board(board, chess.WHITE) - evaluate_board(board, chess.BLACK)


def generate_legal_zh_moves(board):
	moves = list(zh_board.legal_moves) # Get all the standard moves

	for sq in zh_board.legal_drop_squares(): # All the legal squares that can receive a piece
		for droppable_piece in zh_board.pockets[zh_board.turn]: # All the droppable pieces for the current player
			moves.append(chess.Move(from_square=sq, to_square=sq, drop=droppable_piece)) # Add those as move options

	return moves

def best_move(board):
	alpha = -1000000;
    beta = 1000000;
    tp_table = {} # We don't need to evaluate the same board twice.  Essentially memoization for a chess engine

    best_move = None
    best_move_score = -100000

    for move in generate_legal_zh_moves(board):
		score = perform_tree_search_(board, DESIRED_DEPTH, True, alpha, beta, tp_table)
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

    return (best_move, best_move_score)

# Performs AB minimax search given a depth, player, a, b, and transposition table
# Based on https://github.com/rselwyn/tactic-generator/blob/master/src/engine.cpp#L167
def perform_tree_search_(board, depth, isMaximizing, alpha, beta, tp_table):
	if depth == 0:
		return evaluate_(board)

	if board.fen() in tp_table:
		return tp_table[board.fen()] # memoization

	if isMaximizing:
		bestValue = - LARGE_NUM
		possibleMoves = []
		for candidate_move in generate_legal_zh_moves(board):
			board.push(candidate_move)
			minimax_result = perform_tree_search_(board, depth - 1, not isMaximizing, alpha, beta, tp_table)
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
			board.push(candidate_move)
			minimax_result = perform_tree_search_(board, depth - 1, not isMaximizing, alpha, beta, tp_table)
			bestValue = min(bestValue, minimax_result)
			beta = min(beta, bestValue)
			board.pop()

			if beta < alpha:
				break

		tp_table[board.fen()] = bestValue
		return bestValue


zh_board = chess.variant.CrazyhouseBoard()

print(evaluate_(zh_board))
