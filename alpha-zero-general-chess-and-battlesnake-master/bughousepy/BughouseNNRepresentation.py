import numpy as np
import chess
from chess_utils.utils import *

all_possible_moves = create_uci_labels(include_drops=True) # List of all possible moves
num_possible_moves = len(all_possible_moves) # Total number of possible moves

move_to_index = {x:i for i,x in enumerate(all_possible_moves)} # dictionary for fast conversion from string to index

def board_to_input(board):
    """Converts BughouseBoard to ndarray input representation
    """

    player = np.full((1, 8, 8), board.turn) # (1, 8, 8)

    if board.get_active_board().turn == chess.BLACK:
        board = board.mirror()

    active_board = np.full((1, 8, 8), board.active_board) # (1, 8, 8)

    b1_history = to_planes(board.first_board) # (12, 8, 8)
    b2_history = to_planes(board.second_board) # (12, 8, 8)

    b1_prisoners = prisoners(board.first_board) # (10, 8, 8)
    b2_prisoners = prisoners(board.second_board) # (10, 8, 8)

    b1_aux = aux_planes(board.first_board, add_promoted=True) # (7, 8, 8)
    b2_aux = aux_planes(board.second_board, add_promoted=True) # (7, 8, 8)

    ret = np.vstack((player, active_board, b1_history, b2_history, b1_prisoners, b2_prisoners, b1_aux, b2_aux))

    assert ret.shape == (60, 8, 8)
    return ret