import numpy as np
import pandas as pd
import chess
import re
from os import path
import traceback
import lib.BughouseBoard as BughouseBoard
import lib.BughouseGame
import util
import time
import pickle

DATA_DIR = r"..\..\data\bughouse-db"


def load_data_from_text(txt):
    txt = txt.replace('\n', '')
    txt = txt.split('Event')
    last = txt[-1].strip()
    txt = '\n'.join(txt)
    games_moves = re.findall(r' at http://www.bughouse-db\.org}(.*)\[', txt)
    last = re.findall(r' at http://www.bughouse-db\.org}(.*)', last)[0]
    games_moves.append(last)
    return games_moves


def clean_moves(games_moves):
    print("Cleaning games")
    out = []
    for i, moves in enumerate(games_moves):
        if moves[-1] == '*' or '1/2-1/2' in moves:
            continue
        moves_string = moves.replace(re.search(r'{(?:.(?!{))+$', moves).group(0), "").strip()
        moves_seq = moves_string.split("{")
        moves_seq2 = [move for move in moves_seq if 'C:' not in move]
        moves_string2 = "{".join(moves_seq2).strip()
        out.append((moves[-3:], moves_string2))
        # if moves_string != moves_string2:
        #     print(moves_string, moves_string2)
        # if "C:" in moves_string:
        #     print(i, moves_string)
        #     print(len(moves_seq))
        #     # print(moves_seq)
        #     # print('\n')
        #     # print(moves_seq2)
        #     print(len(moves_seq2))
        #     print(len(moves_string2.split(" ")))
        #     print(moves_string2.split(" "))
        #     # print(moves_string2)
        #     assert False
    return out


def load_data_from_file(file):
    txt = open(file).read()
    games_moves = load_data_from_text(txt)
    games_moves = clean_moves(games_moves)
    return games_moves


def calculate_state_value(board_num, reward, game_result, game_length, discount_rate=0.99):
    return reward + discount_rate ** (game_length - board_num - 1) * game_result


def generate_boards_and_values_from_moves(board, moves, result):
    moves = moves.split(" ")
    assert len(moves) / 2 % 1 == 0

    boards = []
    values = []
    board.reset()
    boards.append(lib.BughouseGame.toArray(board))
    values.append(0)

    for i in range(len(moves) // 2):
        board_num = int(moves[2*i][-2].lower() == 'b')
        # team = int(moves[2*i][-2].isupper())
        move = moves[2*i+1]
        assert len(move) != 3, print(move)
        # print(move)
        timing = re.search(r"{(.*?)}", move)
        if timing is None:
            print(move, moves)
            assert False
        move = move.replace(timing.group(0), "")
        move = board.parse_san(board_num, move)
        board.move(board_num, move)
        boards.append(lib.BughouseGame.toArray(board))
        values.append(calculate_state_value(board_num=i, reward=0, game_result=result,
                                            game_length=len(moves) // 2, discount_rate=0.99))
    return boards, values


def build_state_value_dataset(file):
    print("Loading data")
    games_moves = load_data_from_file(file)
    board = BughouseBoard.BughouseBoard()
    data_dict = {}
    times = []
    print("Building dataset")
    for i, (result, moves) in enumerate(games_moves):
        t = time.time()
        result = 2 * int(result[0]) - 1
        boards, values = generate_boards_and_values_from_moves(board, moves, result)
        for i, b in enumerate(boards):
            state = util.hash_state(b.flatten())
            if state not in data_dict.keys():
                data_dict[state] = [values[i]]
            else:
                data_dict[state].append(values[i])
        times.append(time.time() - t)
        if i % 100 == 0:
            print(i, f"{i / len(games_moves) * 100}% complete")
            print(f"Time taken: {np.sum(times)}, average time per game: {np.mean(times)} estimated time left: {(len(games_moves) - i + 1) * np.mean(times)}, estimated total time: {len(games_moves) * np.mean(times)}")

    for i, (state, values) in enumerate(data_dict.items()):
        data_dict[state] = [np.mean(values)]

    return data_dict


def save_dataset_as_csv(data_dict, save_path):
    df = pd.DataFrame(data_dict)
    df.to_csv(save_path, index=False)


def save_dataset_as_pickle(data_dict, save_path):
    with open(save_path, 'wb') as file:
        pickle.dump(data_dict, file)


def open_pickle_dataset(save_path):
    with open(save_path, 'rb') as file:
        return pickle.load(file)


if __name__ == '__main__':
    filename = "test"
    file = path.join(DATA_DIR, "bpgn", f"{filename}.bpgn")
    dataset_dict = build_state_value_dataset(file)
    save_path = path.join(DATA_DIR, "pk", f"{filename}.csv")
    save_dataset_as_pickle(dataset_dict, save_path=save_path)
    # d = open_pickle_dataset(save_path)
    # for k, v in dataset_dict.items():
    #     assert dataset_dict[k] == d[k]
    # k = list(dataset_dict.keys())[0]
    # print(k, dataset_dict[k])

