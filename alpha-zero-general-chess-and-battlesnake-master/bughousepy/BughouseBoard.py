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

    def __init__(self, first_board=None, second_board=None):

        if first_board is None:
            first_board = CrazyhouseBoard()

        if second_board is None:
            second_board = CrazyhouseBoard()

        self.boards = {
            FIRST_BOARD: first_board,
            SECOND_BOARD: second_board,
        }

        self.active_board = FIRST_BOARD

        # Tracking half moves since board.mirror() clears the move stack
        self.half_move_counts = {
            FIRST_BOARD: 0,
            SECOND_BOARD: 0,
        }

    @property
    def first_board(self):
        return self.boards[FIRST_BOARD]
    
    @property
    def second_board(self):
        return self.boards[SECOND_BOARD]

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
        orig_turn = board.turn

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
        # first_white_pocket = self.boards[FIRST_BOARD].pockets[chess.WHITE]
        # first_black_pocket = self.boards[FIRST_BOARD].pockets[chess.BLACK]
        # second_white_pocket = self.boards[SECOND_BOARD].pockets[chess.WHITE]
        # second_black_pocket = self.boards[SECOND_BOARD].pockets[chess.BLACK]
        # pockets = [first_white_pocket, first_black_pocket, second_white_pocket, second_black_pocket]
        # pockets = [str(pocket) for pocket in pockets]
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
                if not check_crazyhouse_draw(other_board):
                    other_board.pockets[board.turn].add(capture_piece_type)#and do bughouse pocket rules
        else:
            board.push(move)

        self.half_move_counts[board_num] += 1
        
        # if board.result() == "1/2-1/2" or other_board.result() == "1/2-1/2":
        #     print("FIRST BOARD:", self.first_board.result())
        #     print("SECOND BOARD:", self.second_board.result())

        if check_crazyhouse_draw(board) and not check_crazyhouse_draw(other_board):
            other_board.turn = orig_turn
            self.active_board = other_board_num

        elif self.first_board.turn != self.second_board.turn and not check_crazyhouse_draw(other_board):
            self.active_board = other_board_num

        # if self.first_board.turn != self.second_board.turn:
        #     self.active_board = other_board_num

        #print("after", board.fen())

    def get_active_board(self):
        return self.boards[self.active_board]

    def copy(self):
        
        new_board = BughouseBoard(self.first_board.copy(), self.second_board.copy())
        new_board.active_board = self.active_board
        new_board.half_move_counts[FIRST_BOARD] = self.half_move_counts[FIRST_BOARD]
        new_board.half_move_counts[SECOND_BOARD] = self.half_move_counts[SECOND_BOARD]

        return new_board

    def mirror(self):
        # Returns a mirrored version of the Bughouse board where the board numbers and colors are swapped

        new_board = BughouseBoard(self.second_board.mirror(), self.first_board.mirror())
        new_board.active_board = not(self.active_board)
        new_board.half_move_counts[FIRST_BOARD] = self.half_move_counts[SECOND_BOARD]
        new_board.half_move_counts[SECOND_BOARD] = self.half_move_counts[FIRST_BOARD]

        return new_board

    @property
    def turn(self):
        if self.active_board == FIRST_BOARD:
            return self.first_board.turn
        else:
            return not(self.second_board.turn)

    def result(self):

        r1 = self.first_board.result()
        r2 = self.second_board.result()

        if r1 == "1-0" or r2 == "0-1":
            return "1-0"
        elif r1 == "0-1" or r2 == "1-0":
            return "0-1"
        elif check_crazyhouse_draw(self.first_board) and check_crazyhouse_draw(self.second_board):
            return "1/2-1/2"
        else:
            return "*"

    def string_rep(self):
        first_board = self.boards[FIRST_BOARD]
        second_board = self.boards[SECOND_BOARD]
        return  ' '.join(first_board.fen().split(' ')[:-1]) + f' {self.half_move_counts[FIRST_BOARD]//2} ' \
            + ' '.join(second_board.fen().split(' ')[:-1]) + f' {self.half_move_counts[SECOND_BOARD]//2} ' \
                + str(int(self.active_board))

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

def check_crazyhouse_draw(board: CrazyhouseBoard):
    return board.result() == "1/2-1/2" or board.halfmove_clock >= 75

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