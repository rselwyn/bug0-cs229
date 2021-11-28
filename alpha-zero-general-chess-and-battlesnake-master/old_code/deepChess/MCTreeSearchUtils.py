import random

import chess
from deepChess import ChessUtils
from deepChess.Agent import Agent

MAX_SCORE = 1000
MIN_SCORE = -1000


class MCTSNode(object):
    def __init__(self, game_state, parent=None, move=None):
        self.game_state = game_state
        self.parent = parent
        self.move = move
        self.win_counts = {
            ChessUtils.Winner.WHITE: 0,
            ChessUtils.Winner.BLACK: 0,
            ChessUtils.Winner.DRAW: 0,
        }
        self.num_rollouts = 0
        self.children = []
        self.unvisited_moves = game_state.possible_moves()

    def add_random_child(self):
        index = random.randint(0, len(self.unvisited_moves) - 1)
        new_move = self.unvisited_moves.pop(index)
        # TODO maybe fix this for chess
        new_game_state = self.game_state.copy()
        new_game_state.step(new_move)
        new_node = MCTSNode(new_game_state, self, new_move)
        self.children.append(new_node)
        return new_node

    def record_win(self, winner):
        self.win_counts[winner] += 1
        self.num_rollouts += 1

    def can_add_child(self):
        return len(self.unvisited_moves) > 0

    def is_terminal(self):
        return self.game_state.done

    def winning_frac(self, player):
        return float(self.win_counts[player]) / float(self.num_rollouts)


def show_tree(node, indent='', max_depth=3):
    if max_depth < 0:
        return
    if node is None:
        return
    if node.parent is None:
        print('%sroot' % indent)
    else:
        player = node.parent.game_state.next_player()
        move = node.move
        print('%s%s %s %d %.3f' % (
            indent, player, move,
            node.num_rollouts,
            node.winning_frac(player),
        ))
    for child in sorted(node.children, key=lambda n: n.num_rollouts, reverse=True):
        show_tree(child, indent + '  ', max_depth - 1)