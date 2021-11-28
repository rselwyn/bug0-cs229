import time

from deepChess.ChessUtils import MyChessEnv
from deepChess.RandomAgent import RandomBot
from deepChess.MCTSAgent import MCTSBot


def main():
    game = MyChessEnv(debug=False)

    player1 = MCTSBot(800,1.5)
    player2 = RandomBot()

    while not game.done:
        time.sleep(0.5)
        # clear screen
        print(chr(27) + "[2J")
        if game.white_to_move:
            move = player1.select_move(game)
            game.step(move)
        else:
            move = player2.select_move(game)
            game.step(move)
        game.render()

    print("Result final winner: ", game.winner)


if __name__ == '__main__':
    main()
