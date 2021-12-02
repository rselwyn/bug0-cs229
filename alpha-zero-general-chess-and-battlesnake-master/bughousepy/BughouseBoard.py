"""
All implementation credit for this goes to https://github.com/AnishN/bugaboo/blob/master/bughouse.py, under fair use within
the MIT license.
"""

import re
from enum import Enum
from chess.variant import CrazyhouseBoard, CrazyhousePocket
import chess
import numpy as np

FIRST_BOARD = 0
SECOND_BOARD = 1

class BughouseBoard(object):

    def __init__(self, first_board=None, second_board=None, active_board=FIRST_BOARD):

        if first_board is None:
            first_board = CrazyhouseBoard()

        if second_board is None:
            second_board = CrazyhouseBoard()

        self.boards = {
            FIRST_BOARD: first_board,
            SECOND_BOARD: second_board,
        }

        self.first_board = first_board
        self.second_board = second_board

        self.active_board = active_board

    def reset(self):
        first_board = self.boards[FIRST_BOARD]
        second_board = self.boards[SECOND_BOARD]
        first_board.set_fen(chess.STARTING_FEN)
        second_board.set_fen(chess.STARTING_FEN)
        self.active_board = FIRST_BOARD

    def move(self, move):

        board_num = self.active_board

        #print(move_number, san, board_num)
        other_board_num = not(board_num)
        board = self.boards[board_num]
        other_board = self.boards[other_board_num]

        # print(board)
        # print("Turn:", board.turn)
        # print("White:")
        # print(bitboard_to_array(board.occupied_co[chess.WHITE]))
        # print("Black:")
        # print(bitboard_to_array(board.occupied_co[chess.BLACK]))
        # touched = chess.BB_SQUARES[move.from_square] ^ chess.BB_SQUARES[move.to_square]
        # print("Touched:")
        # print(bitboard_to_array(touched))
        # print("Capture:")
        # print(bitboard_to_array(touched & board.occupied_co[not board.turn]))
        is_capture = board.is_capture(move)
        # print("Is Capture:", is_capture)
        #is_castling = board.is_castling(move)
        capture_piece_type = None
        #print(board_num, move.from_square, move.to_square)#, is_castling)
        #print("before", board.fen())
        #print(is_capture, move.drop)
        first_white_pocket = self.boards[FIRST_BOARD].pockets[chess.WHITE]
        first_black_pocket = self.boards[FIRST_BOARD].pockets[chess.BLACK]
        second_white_pocket = self.boards[SECOND_BOARD].pockets[chess.WHITE]
        second_black_pocket = self.boards[SECOND_BOARD].pockets[chess.BLACK]
        pockets = [first_white_pocket, first_black_pocket, second_white_pocket, second_black_pocket]
        pockets = [str(pocket) for pocket in pockets]
        #print(pockets)
        if is_capture:
            if move.drop != None:
                board.pockets[board.turn].remove(move.drop)
                board.push(move)
            else:
                capture_piece = board.piece_at(move.to_square)
                if capture_piece == None:
                    if board.is_en_passant(move):
                        capture_piece_type = chess.PAWN
                else:
                    capture_piece_type = capture_piece.piece_type
                if board.promoted & (1 << move.to_square):
                    capture_piece_type = chess.PAWN
                board.push(move)
                board.pockets[not(board.turn)].remove(capture_piece_type)#undo crazyhouse pocket rules
                other_board.pockets[board.turn].add(capture_piece_type)#and do bughouse pocket rules
        else:
            board.push(move)
        
        if self.first_board.turn != self.second_board.turn:
            self.active_board = other_board_num

        #print("after", board.fen())

    def get_active_board(self):
        return self.boards[self.active_board]

    def copy(self):
        return BughouseBoard(self.first_board.copy(), self.second_board.copy())

    def mirror(self):
        # Returns a mirrored version of the Bughouse board where the board numbers and colors are swapped
        return BughouseBoard(self.second_board.mirror(), self.first_board.mirror(), not(self.active_board))

    @property
    def turn(self):
        if self.active_board == FIRST_BOARD:
            return self.first_board.turn
        else:
            return not(self.second_board.turn)

    def get_fens(self):
        first_board = self.boards[FIRST_BOARD]
        second_board = self.boards[SECOND_BOARD]
        return (first_board.fen(), second_board.fen())

    def in_sync(self):
        # We assume that the bot is playing black on board 1 and white on board 2, and that the first player has made their move
        return self.boards[FIRST_BOARD].ply() == self.boards[SECOND_BOARD].ply() + 1

    def visualize(self):
        first_board = str(self.boards[FIRST_BOARD]).split('\n')
        second_board = str(self.boards[SECOND_BOARD]).split('\n')
        output = ""
        for i in range(8):
            output += first_board[i] + "    " + second_board[7-i] + '\n'
        return output[:-1]

    def parse_san(self, board_num, san):
        return self.boards[board_num].parse_san(san)

def bitboards_to_array(bb: np.ndarray) -> np.ndarray:
    bb = np.asarray(bb, dtype=np.uint64)[:, np.newaxis]
    s = 8 * np.arange(7, -1, -1, dtype=np.uint64)
    b = (bb >> s).astype(np.uint8)
    b = np.unpackbits(b, bitorder="little")
    return b.reshape(-1, 8, 8)

def bitboard_to_array(bb: int) -> np.ndarray:
    s = 8 * np.arange(7, -1, -1, dtype=np.uint64)
    b = (bb >> s).astype(np.uint8)
    b = np.unpackbits(b, bitorder="little")
    return b.reshape(8, 8)