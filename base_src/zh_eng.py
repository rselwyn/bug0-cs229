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

ALL_PIECES = [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.KING, chess.QUEEN]

def evaluate_board(board, color):
	eval_score_curr_player = 100 # Total Eval Score for the current position.  Start at 100 just to ensure > 0

	for piece in ALL_PIECES:
		for piece_instance in board.pieces(piece, color):
			eval_score_curr_player += piece_values[piece]

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


zh_board = chess.variant.CrazyhouseBoard()

print(evaluate_(zh_board))
