import numpy as np
import pandas as pd
import chess
import re
from os import path
import traceback
from lib import bughouse

DATA_DIR = r"C:\Users\abhay\Documents\Stanford\CS229\project\data\bughouse-db"


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
    out_dict = {}
    for i, moves in enumerate(games_moves):
        if moves[-1] == '*' or '1/2-1/2' in moves:
            continue
        out_dict[moves[-3:]] = moves.replace(re.search(r'{(?:.(?!{))+$', moves).group(0), "").strip()
        print(i)
    return out_dict


def generate_boards_from_moves(board, moves):
    moves = moves.split(" ")
    assert len(moves) / 2 % 1 == 0

    boards = []
    board.reset()
    boards.append(board.get_fens())

    for i in range(len(moves) // 2):
        board_num = int(moves[i][-1].lower() == 'b')
        move = moves[i+1].replace(re.search(r"{(.*?)}", moves[i+1]).group(0), "")
        move = board.parse_san(move)
        board.move(board_num, move)
        boards.append(board.get_fens())
    return boards


def build_state_value_dataset(file):
    games_moves = load_data_from_file(file)
    board = bughouse.BughouseBoard()
    data_dict = {}
    for i, (result, moves) in enumerate(games_moves.items()):
        states = generate_boards_from_moves(board, moves)
        for i, state in enumerate(states):
            data_dict[state] = 0
            if i == len(states)-1:
                data_dict[state] = 2 * int(result[0]) - 1
    return data_dict


def save_dataset_as_pandas(data_dict):
    pass

def load_data_from_file(file):
    txt = open(file).read()
    games_moves = load_data_from_text(txt)
    games_moves = clean_moves(games_moves)
    return games_moves

if __name__ == '__main__':
    file = path.join(DATA_DIR, "export2018.bpgn")
    dataset_dict = build_state_value_dataset(file)
    k = list(dataset_dict.keys())[0]
    print(k, dataset_dict[k])

