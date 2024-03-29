import chess
import chess.variant
from .BughouseBoard import BughouseBoard
from .BughouseNNRepresentation import num_possible_moves, all_possible_moves, move_to_index
import numpy as np
from Game import Game

# noinspection SpellCheckingInspection

# Code motivated/based on https://github.com/Zeta36/chess-alpha-zero/blob/master/src/chess_zero/env/chess_env.py

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
        return num_possible_moves

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
            board = board.copy()
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
        
        current_allowed_moves = [move.uci() for move in board.get_active_board().legal_moves]

        validMoves = np.zeros((self.getActionSize(),))
        for x in current_allowed_moves:
            validMoves[move_to_index[x]] = 1

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

        r = board.result()

        if r == "1-0":
            return player
        elif r == "0-1":
            return -player
        elif r == "1/2-1/2":
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

        return board.string_rep()

    @staticmethod
    def display(board, visualize=True, string_rep=False, result=False):
        if visualize:
            print(board.visualize())
        if string_rep:
            print(board.string_rep())
        if result:
            print(board.first_board.result(), board.second_board.result())

def libPlayerToBughousePlayer(turn):
    return 1 if turn else -1
