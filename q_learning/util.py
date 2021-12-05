import numpy as np


def hash_state_to_int(state):
    state = state.astype(int)
    s = ''.join(list(map(str, state)))
    print(f"string s: {s}")
    return int(s, base=2), len(s)


def unhash_state_from_int(i, state_length):
    s = f'{i:{state_length}b}'
    s = np.array(list(s), dtype=float)
    return s


def hash_state_to_string(state):
    state = state.astype(int)
    s = ''.join(list(map(str, state)))
    return s


def unhash_state_from_string(s):
    s = np.array(list(s), dtype=float)
    return s


def hash_state(state):
    return hash_state_to_string(state)


def unhash_state(hashed):
    return unhash_state_from_string(hashed)
