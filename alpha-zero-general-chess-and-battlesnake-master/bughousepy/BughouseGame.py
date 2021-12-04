import chess
import chess.variant
from .BughouseBoard import BughouseBoard
import numpy as np
from .BughouseConstants import all_possible_moves, all_possible_moves_dict, all_possible_moves_num

from Game import Game

# noinspection SpellCheckingInspection

# Code motivated/based on https://github.com/Zeta36/chess-alpha-zero/blob/master/src/chess_zero/env/chess_env.py

# input planes
pieces_order = 'KQRBNPkqrbnp'  # 12x8x8
castling_order = 'KQkq'  # 4x8x8
# fifty-move-rule             # 1x8x8
# en en_passant               # 1x8x8
ind = {pieces_order[i]: i for i in range(12)}

class BughouseGame(Game):
    """
    This class specifies the Chess Game class. This works when the game is
    two-player, adversarial and turn-based.

    Use 1 for player1 and -1 for player2.

    """

    def __init__(self):
        super().__init__()

    def getInitBoard(self):
        """
        Returns:
            startBoard: a representation of the board (ideally this is the form
                        that will be the input to your neural network)
        """
        # create input layers with fresh board
        # return create_input_planes(self.board.fen())
        board = BughouseBoard()
        return board

    def getBoardSize(self):
        """
        Returns:
            (x,y): a tuple of board dimensions
        """
        return (60, 8, 8)

    def getActionSize(self):
        """
        Returns:
            actionSize: number of all possible actions
        """
        return all_possible_moves_num

    def getNextState(self, board, player, action):
        """
        Input:
            board: current board
            player: current player (1 or -1)
            action: action taken by current player

        Returns:
            nextBoard: board after applying action
            nextPlayer: player who plays in the next turn (should be -player)
        """
        # TODO remove assert not required part for speed
        # assert libPlayerToBughousePlayer(board.turn) == player
        
        move = all_possible_moves[action]
        
        if board.get_active_board().turn == chess.BLACK:
            board = board.mirror()
            board.move(chess.Move.from_uci(move))
            board = board.mirror()
        
        else:
            board.move(chess.Move.from_uci(move))

        return (board, -player)

    def getValidMoves(self, board, player):
        """
        Input:
            board: current board
            player: current player

        Returns:
            validMoves: a binary vector of length self.getActionSize(), 1 for
                        moves that are valid from the current board and player,
                        0 for invalid moves
        """
        # TODO remove assert not required part for speed
        # assert libPlayerToBughousePlayer(board.turn) == player

        if board.get_active_board().turn == chess.BLACK:
            board = board.mirror()
        
        current_allowed_moves = getAllowedMovesFromBoard(board)

        validMoves = np.zeros((all_possible_moves_num,))
        for x in current_allowed_moves:
            validMoves[all_possible_moves_dict[x]] = 1

        # if np.sum(validMoves) != len(current_allowed_moves):
        #     print(current_allowed_moves)
        #     print([x for x in current_allowed_moves if x in all_possible_moves])
        #     assert False
        
        return validMoves

    def getGameEnded(self, board, player):
        """
        Input:
            board: current board
            player: current player (1 or -1)

        Returns:
            r: 0 if game has not ended. 1 if player won, -1 if player lost,
               small non-zero value for draw.

        """

        r1 = board.first_board.result()
        r2 = board.second_board.result()

        if r1 == "1-0" or r2 == "0-1":
            return player
        elif r1 == "0-1" or r2 == "1-0":
            return -player
        elif r1 == "1/2-1/2" and r2 == "1/2-1/2":
            return 1e-4  # TODO how small is better?
        else:
            return 0

    def getCanonicalForm(self, board, player):
        """
        Input:
            board: current board
            player: current player (1 or -1)

        Returns:
            canonicalBoard: returns canonical form of board. The canonical form
                            should be independent of player. For e.g. in chess,
                            the canonical form can be chosen to be from the pov
                            of white. When the player is white, we can return
                            board as is. When the player is black, we can invert
                            the colors and return the board.
        """
        # TODO remove assert not required part for speed
        # assert libPlayerToBughousePlayer(board.turn) == player
        
        # print("Active board:", int(board.active_board))
        # print("Active board turn:", "White" if board.get_active_board().turn else "Black")
        # print("Game turn:", "Player 1" if board.turn else "Player -1")
        # print("Player:", int(player))

        return board

    def getSymmetries(self, board, pi):
        """
        Input:
            board: current board
            pi: policy vector of size self.getActionSize()

        Returns:
            symmForms: a list of [(board,pi)] where each tuple is a symmetrical
                       form of the board and the corresponding pi vector. This
                       is used when training the neural network from examples.
        """
        return [(board, pi)]

    def stringRepresentation(self, board):
        """
        Input:
            board: current board

        Returns:
            boardString: a quick conversion of board to a string format.
                         Required by MCTS for hashing.
        """
        # # TODO maybe player move matters?
        # fen = board.fen()
        # # l = fen.rindex(' ', fen.rindex(' '))
        # # return fen[0:l]
        # parts = board.fen().split(' ')
        # return parts[0] + ' ' + parts[2] + ' ' + parts[3]

        return board.first_board.fen() + board.second_board.fen() + " " + str(int(board.active_board))

    @staticmethod
    def display(board):
        print(board.visualize())

    def toArray(self, board):
        # fen = board.fen()
        # fen = maybe_flip_fen(fen, is_black_turn(fen))
        return all_input_planes(board)


# def mirror_action(action):
#     return chess.Move(chess.square_mirror(action.from_square), chess.square_mirror(action.to_square))


def getAllowedMovesFromBoard(board):
    return [move.uci() for move in board.get_active_board().legal_moves]


# reverse the fen representation as if black is white and vice-versa
# def maybe_flip_fen(fen, flip=False):
#     if not flip:
#         return fen
#     foo = fen.split(' ')
#     rows = foo[0].split('/')

#     return "/".join([swapall(row) for row in reversed(rows)]) \
#            + " " + ('w' if foo[1] == 'b' else 'b') \
#            + " " + "".join(sorted(swapall(foo[2]))) \
#            + " " + foo[3] + " " + foo[4] + " " + foo[5]


# def is_black_turn(fen):
#     return fen.split(" ")[1] == 'b'


def all_input_planes(board):

    player = np.full((1, 8, 8), board.turn) # (1, 8, 8)

    if board.get_active_board().turn == chess.BLACK:
        board = board.mirror()

    active_board = np.full((1, 8, 8), board.active_board) # (1, 8, 8)

    b1_history = to_planes(board.first_board) # (12, 8, 8)
    b2_history = to_planes(board.second_board) # (12, 8, 8)

    b1_prisoners = prisoners(board.first_board) # (10, 8, 8)
    b2_prisoners = prisoners(board.second_board) # (10, 8, 8)

    b1_aux = aux_planes(board.first_board) # (7, 8, 8)
    b2_aux = aux_planes(board.second_board) # (7, 8, 8)

    ret = np.vstack((player, active_board, b1_history, b2_history, b1_prisoners, b2_prisoners, b1_aux, b2_aux))

    assert ret.shape == (60, 8, 8)
    return ret


# Create layers for
# castling_order = 'KQkq'     # 4x8x8
# fifty-move-rule             # 1x8x8
# en en_passant               # 1x8x8

def aux_planes(board):

    fen = board.fen()

    foo = fen.split(' ')

    promoted = bitboard_to_array(board.promoted())

    en_passant = np.zeros((8, 8), dtype=np.float32)
    if foo[3] != '-':
        eps = alg_to_coord(foo[3])
        en_passant[eps[0]][eps[1]] = 1

    fifty_move_count = int(foo[4])
    fifty_move = np.full((8, 8), fifty_move_count, dtype=np.float32)

    castling = foo[2]
    auxiliary_planes = [np.full((8, 8), int('K' in castling), dtype=np.float32),
                        np.full((8, 8), int('Q' in castling), dtype=np.float32),
                        np.full((8, 8), int('k' in castling), dtype=np.float32),
                        np.full((8, 8), int('q' in castling), dtype=np.float32),
                        fifty_move,
                        en_passant,
                        promoted]

    ret = np.asarray(auxiliary_planes, dtype=np.float32)
    assert ret.shape == (7, 8, 8)
    return ret


# create layers for pieces in order = 'KQRBNPkqrbnp'  # 12x8x8
# def to_planes(fen):
#     board_state = replace_tags_board(fen)
#     pieces_both = np.zeros(shape=(12, 8, 8), dtype=np.float32)
#     for rank in range(8):
#         for file in range(8):
#             v = board_state[rank * 8 + file]
#             if v.isalpha():
#                 pieces_both[ind[v]][rank][file] = 1
#     assert pieces_both.shape == (12, 8, 8)
#     return pieces_both

def to_planes(board):

    black, white = board.occupied_co

    bitboards = np.array([
        white & board.kings,
        white & board.queens,
        white & board.rooks,
        white & board.bishops,
        white & board.knights,
        white & board.pawns,
        black & board.kings,
        black & board.queens,
        black & board.rooks,
        black & board.bishops,
        black & board.knights,
        black & board.pawns,
    ], dtype=np.uint64)

    return bitboards_to_array(bitboards)

def prisoners(board):

    counts = np.zeros(10)

    for i, c in enumerate((chess.WHITE, chess.BLACK)):
        pocket = board.pockets[c]
        for j, p in enumerate((chess.QUEEN, chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN)):
            counts[5*i+j] = pocket.count(p)

    return np.broadcast_to(counts[...,None,None], (10, 8, 8))

# def replace_tags_board(board_san):
#     board_san = board_san.split(" ")[0]
#     board_san = board_san.replace("2", "11")
#     board_san = board_san.replace("3", "111")
#     board_san = board_san.replace("4", "1111")
#     board_san = board_san.replace("5", "11111")
#     board_san = board_san.replace("6", "111111")
#     board_san = board_san.replace("7", "1111111")
#     board_san = board_san.replace("8", "11111111")
#     return board_san.replace("/", "")


def alg_to_coord(alg):
    rank = 8 - int(alg[1])  # 0-7
    file = ord(alg[0]) - ord('a')  # 0-7
    return rank, file


# def swapcase(a):
#     if a.isalpha():
#         return a.lower() if a.isupper() else a.upper()
#     return a


# def swapall(aa):
#     return "".join([swapcase(a) for a in aa])


def libPlayerToBughousePlayer(turn):
    return 1 if turn else -1

# https://chess.stackexchange.com/questions/29294/quickly-converting-board-to-bitboard-representation-using-python-chess-library

def bitboard_to_array(bb: int) -> np.ndarray:
    s = 8 * np.arange(7, -1, -1, dtype=np.uint64)
    b = (bb >> s).astype(np.uint8)
    b = np.unpackbits(b, bitorder="little")
    return b.reshape(8, 8)

def bitboards_to_array(bb: np.ndarray) -> np.ndarray:
    bb = np.asarray(bb, dtype=np.uint64)[:, np.newaxis]
    s = 8 * np.arange(7, -1, -1, dtype=np.uint64)
    b = (bb >> s).astype(np.uint8)
    b = np.unpackbits(b, bitorder="little")
    return b.reshape(-1, 8, 8)