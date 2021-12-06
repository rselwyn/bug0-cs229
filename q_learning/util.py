import numpy as np
import tqdm


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


def dataset_to_array(data_dict, tqdm, max_n=None):
    states = []
    values = []
    iter_max = len(data_dict.keys())
    if max_n < iter_max:
        iter_max = max_n

    with tqdm(total=iter_max) as pbar:
        for i, (state_hash, value) in enumerate(data_dict.items()):
            state = unhash_state(state_hash)
            if state.shape[0] != 3840:
                pbar.update(1)
                continue
            states.append(state)
            values.append(np.mean(value))
            pbar.update(1)
            if i >= iter_max-1:
                break
    assert len(states) == len(values)
    states = np.stack(states).astype(np.int8)
    values = np.stack(values)
    return states, values


