import chess.variant

def find_best_move(board):
	pass

def evaluate_board(board):
	pass

def generate_legal_zh_moves(board):
	moves = list(zh_board.legal_moves) # Get all the standard moves

	for sq in zh_board.legal_drop_squares(): # All the legal squares that can receive a piece
		for droppable_piece in zh_board.pockets[zh_board.turn()]: # All the droppable pieces for the current player
			moves.append(chess.Move(from_square=sq, to_square=sq, drop=droppable_piece)) # Add those as move options

	return moves


zh_board = chess.variant.CrazyhouseBoard()