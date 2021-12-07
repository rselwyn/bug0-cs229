# Arena for Classical Engine vs NN Engine
import bug_eng as bug
import lib.bughouse as bug_board

import math

import chess

NUM_GAMES_TO_RUN = 10 
OUTPUT_FOLDER = "head_to_head_games/"
GAME_PREFIX = "game_"

TREE_DEPTH = 5

def calculate_elo_diff(wins, losses, draws):
	# adopted from https://www.3dkingdoms.com/chess/elo.htm

	score = wins + draws / 2
	total = wins + draws + losses
	percentage = score / total
	return -400 * math.log10(1 / percentage - 1)

def handle_log(board):
	pass

wins_team_1 = 0
losses_team_1 = 0

for game_number in range(NUM_GAMES_TO_RUN):
	print("Starting Game #" + str(game_number))

	board = bug_board.BughouseBoard()
	board.move(0, chess.Move.from_uci("e2e4"))

	while not board.is_game_over():
		board.move_tuple(bug.best_move(board, TREE_DEPTH))
		if board.is_game_over():
			# In this case, the classic engine won
			pass
		else:
			pass



assert board.in_sync()