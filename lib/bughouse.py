"""
All implementation credit for this goes to https://github.com/AnishN/bugaboo/blob/master/bughouse.py, under fair use within
the MIT license.
"""

import re
from enum import Enum
from chess.variant import CrazyhouseBoard, CrazyhousePocket
import chess

FIRST_BOARD = 0
SECOND_BOARD = 1

class BughouseBoard(object):

    def __init__(self):
        self.boards = {
            FIRST_BOARD: CrazyhouseBoard(),
            SECOND_BOARD: CrazyhouseBoard(),
        }
        self.reset()

    def reset(self):
        first_board = self.boards[FIRST_BOARD]
        second_board = self.boards[SECOND_BOARD]
        first_board.set_fen(chess.STARTING_FEN)
        second_board.set_fen(chess.STARTING_FEN)

    def move(self, board_num, move):
        #print(move_number, san, board_num)
        other_board_num = not(board_num)
        board = self.boards[board_num]
        other_board = self.boards[other_board_num]

        is_capture = board.is_capture(move)
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
        #print("after", board.fen())

    def get_fens(self):
        first_board = self.boards[FIRST_BOARD]
        second_board = self.boards[SECOND_BOARD]
        return (first_board.fen(), second_board.fen())