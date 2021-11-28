import enum
import chess
import numpy as np
import copy

from logging import getLogger

logger = getLogger(__name__)

class Player(enum.Enum):
    black = 1
    white = 2

    @property
    def other(self):
        return Player.black if self == Player.white else Player.white


Winner = enum.Enum("Winner", "BLACK WHITE DRAW")

pieces_order = 'KQRBNPkqrbnp'

pieces = {pieces_order[i]: i for i in range(12)}

# print(pieces)

class MyChessEnv:
    def __init__(self, debug=True):
        self.board = chess.Board()
        self.moves_count = 0
        self.winner = None  # type: Winner
        self.resigned = False
        self.score = None
        self.debug = debug

    def reset(self):
        self.board = chess.Board()
        self.moves_count = 0
        self.winner = None
        self.resigned = False
        self.score = None
        return self

    def update(self, board):
        self.board = chess.Board(board)
        # TODO check if there is any winner and update the following
        self.winner = None
        self.resigned = False
        self.score = None
        return self

    def _resign(self):
        self.resigned = True
        if self.white_to_move:
            self.winner = Winner.BLACK
            self.score = "0-1"
        else:
            self.winner = Winner.WHITE
            self.score = "1-0"

    def step(self, action: str, check_over=True):
        """
        Takes an action and updates the game state
        :param str action: action to take in uci notation
        :param boolean check_over: whether to check if game is over
        """
        if check_over and action is None:
            self._resign()
            return
        if self.debug:
            if self.white_to_move:
                print(self.moves_count, " White Plays: ", action, " ", self.board.fen())
            else:
                print(self.moves_count, " Black Plays: ", action, " ", self.board.fen())
        self.board.push_uci(action)

        self.moves_count += 1

        if check_over and self.board.result(claim_draw=True) != "*":
            if self.winner is None:
                self.score = self.board.result(claim_draw=True)
                if self.score == '1-0':
                    self.winner = Winner.WHITE
                elif self.score == '0-1':
                    self.winner = Winner.BLACK
                else:
                    self.winner = Winner.DRAW
            else:
                print(" debug there is already a winner!")
        return self

    @property
    def done(self):
        return self.winner is not None

    @property
    def white_won(self):
        return self.winner == Winner.WHITE

    @property
    def white_to_move(self):
        return self.board.turn == chess.WHITE

    def winner(self):
        return self.winner

    def next_player(self):
        if (self.white_to_move):
            return Winner.BLACK
        else:
            return Winner.WHITE

    def observation(self):
        return self.board.fen()

    def copy(self):
        env = copy.copy(self)
        env.board = copy.copy(self.board)
        return env

    def render(self):
        print("\n")
        print(self.board)
        print("\n")

    def possible_moves(self):
        return [move.uci() for move in self.board.legal_moves]

    def undo(self):
        self.board.pop()
        self.moves_count -=1




def is_black_turn(fen):
    return fen.split(" ")[1] == 'b'


def position_evaluation(fen, absolute=False) -> float:
    piece_vals = {'K': 3, 'Q': 14, 'R': 5, 'B': 3.25, 'N': 3, 'P': 1}  # if there is no king game is over already Q=14
    player_points = 0.0
    total_points = 0
    for c in fen.split(' ')[0]:
        if not c.isalpha():
            continue
        # assert c.upper() in piece_vals
        if c.isupper():
            player_points += piece_vals[c]
            total_points += piece_vals[c]
        else:
            player_points -= piece_vals[c.upper()]
            total_points += piece_vals[c.upper()]
    value = player_points / total_points
    if not absolute and is_black_turn(fen):
        value = -value
    assert abs(value) < 1
    return np.tanh(value * 3)  # random function


def position_evaluation_simple(fen, absolute=False) -> float:
    piece_vals = {'K': 90, 'Q': 9, 'R': 5, 'B': 3.25, 'N': 3,
                  'P': 1}  # if there is no king game is over already Q=14
    player_points = 0.0
    count = 0
    for c in fen.split(' ')[0]:
        if not c.isalpha():
            continue
        if c.isupper():
            player_points += piece_vals[c]
            count+=1
        else:
            player_points -= piece_vals[c.upper()]
            count+=1

    if is_black_turn(fen):
        return -1 * player_points
    else:
        return player_points


def reverseArray(inputArray):
    return inputArray[::-1];


pawnEvalWhite =[
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0, 5.0],
    [1.0, 1.0, 2.0, 3.0, 3.0, 2.0, 1.0, 1.0],
    [0.5, 0.5, 1.0, 2.5, 2.5, 1.0, 0.5, 0.5],
    [0.0, 0.0, 0.0, 2.0, 2.0, 0.0, 0.0, 0.0],
    [0.5, -0.5, -1.0, 0.0, 0.0, -1.0, -0.5, 0.5],
    [0.5, 1.0, 1.0, -2.0, -2.0, 1.0, 1.0, 0.5],
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
];

pawnEvalBlack = reverseArray(pawnEvalWhite);

knightEval =[
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0],
    [-4.0, -2.0, 0.0, 0.0, 0.0, 0.0, -2.0, -4.0],
    [-3.0, 0.0, 1.0, 1.5, 1.5, 1.0, 0.0, -3.0],
    [-3.0, 0.5, 1.5, 2.0, 2.0, 1.5, 0.5, -3.0],
    [-3.0, 0.0, 1.5, 2.0, 2.0, 1.5, 0.0, -3.0],
    [-3.0, 0.5, 1.0, 1.5, 1.5, 1.0, 0.5, -3.0],
    [-4.0, -2.0, 0.0, 0.5, 0.5, 0.0, -2.0, -4.0],
    [-5.0, -4.0, -3.0, -3.0, -3.0, -3.0, -4.0, -5.0]
];

bishopEvalWhite = [
    [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0],
    [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 1.0, 1.0, 0.5, 0.0, -1.0],
    [-1.0, 0.5, 0.5, 1.0, 1.0, 0.5, 0.5, -1.0],
    [-1.0, 0.0, 1.0, 1.0, 1.0, 1.0, 0.0, -1.0],
    [-1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, -1.0],
    [-1.0, 0.5, 0.0, 0.0, 0.0, 0.0, 0.5, -1.0],
    [-2.0, -1.0, -1.0, -1.0, -1.0, -1.0, -1.0, -2.0]
];

bishopEvalBlack = reverseArray(bishopEvalWhite);

rookEvalWhite = [
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    [0.5, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [-0.5, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -0.5],
    [0.0, 0.0, 0.0, 0.5, 0.5, 0.0, 0.0, 0.0]
];

rookEvalBlack = reverseArray(rookEvalWhite);

evalQueen = [
    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0],
    [-1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
    [-0.5, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
    [0.0, 0.0, 0.5, 0.5, 0.5, 0.5, 0.0, -0.5],
    [-1.0, 0.5, 0.5, 0.5, 0.5, 0.5, 0.0, -1.0],
    [-1.0, 0.0, 0.5, 0.0, 0.0, 0.0, 0.0, -1.0],
    [-2.0, -1.0, -1.0, -0.5, -0.5, -1.0, -1.0, -2.0]
];

kingEvalWhite = [

    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-3.0, -4.0, -4.0, -5.0, -5.0, -4.0, -4.0, -3.0],
    [-2.0, -3.0, -3.0, -4.0, -4.0, -3.0, -3.0, -2.0],
    [-1.0, -2.0, -2.0, -2.0, -2.0, -2.0, -2.0, -1.0],
    [2.0, 2.0, 0.0, 0.0, 0.0, 0.0, 2.0, 2.0],
    [2.0, 3.0, 1.0, 0.0, 0.0, 1.0, 3.0, 2.0]
];


kingEvalBlack = reverseArray(kingEvalWhite);

# def alpha_beta_result(game_state: ChessUtils.MyChessEnv, max_depth,
#                       best_black, best_white, eval_fn):
#     if game_state.done():
#         if game_state.winner() == game_state.next_player:
#             return MAX_SCORE
#         else:
#             return MIN_SCORE
#
#     if max_depth == 0:
#         return eval_fn(game_state)
#
#     best_so_far = MIN_SCORE
#     for candidate_move in game_state.legal_moves():
#         next_state = game_state.apply_move(candidate_move)
#         opponent_best_result = alpha_beta_result(
#             next_state, max_depth - 1,
#             best_black, best_white,
#             eval_fn)
#         our_result = -1 * opponent_best_result
#
#         if our_result > best_so_far:
#             best_so_far = our_result
#         if game_state.next_player == chess.WHITE:
#             if best_so_far > best_white:
#                 best_white = best_so_far
#             outcome_for_black = -1 * best_so_far
#             if outcome_for_black < best_black:
#                 return best_so_far
#         elif game_state.next_player == chess.BLACK:
#             if best_so_far > best_black:
#                 best_black = best_so_far
#             outcome_for_white = -1 * best_so_far
#             if outcome_for_white < best_white:
#                 return best_so_far
#
#     return best_so_far


# def minimax(depth, env: ChessUtils.MyChessEnv, alpha, beta, is_maximizing):
#     if (depth == 0):
#         return -ChessUtils.position_evaluation_simple(env.observation())
#     possibleMoves = env.possible_moves()
#     if (is_maximizing):
#         bestMove = MIN_SCORE
#         for x in possibleMoves:
#             move = chess.Move.from_uci(str(x))
#             env.step(move)
#             bestMove = max(bestMove, minimax(depth - 1, env, alpha, beta, not is_maximizing))
#             env.undo()
#             alpha = max(alpha, bestMove)
#             if beta <= alpha:
#                 return bestMove
#         return bestMove
#     else:
#         bestMove = MAX_SCORE
#         for x in possibleMoves:
#             move = chess.Move.from_uci(str(x))
#             env.step(move)
#             bestMove = min(bestMove, minimax(depth - 1, env, alpha, beta, not is_maximizing))
#             env.undo()
#             beta = min(beta, bestMove)
#             if (beta <= alpha):
#                 return bestMove
#         return bestMove
