import numpy as np
import chess

def create_uci_labels(include_drops=False):
    """
    Creates the labels for the universal chess interface into an array and returns them
    :return:
    """
    labels_array = []
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    numbers = ['1', '2', '3', '4', '5', '6', '7', '8']
    promoted_to = ['q', 'r', 'b', 'n']

    for l1 in range(8):
        for n1 in range(8):
            destinations = [(t, n1) for t in range(8)] + \
                           [(l1, t) for t in range(8)] + \
                           [(l1 + t, n1 + t) for t in range(-7, 8)] + \
                           [(l1 + t, n1 - t) for t in range(-7, 8)] + \
                           [(l1 + a, n1 + b) for (a, b) in
                            [(-2, -1), (-1, -2), (-2, 1), (1, -2), (2, -1), (-1, 2), (2, 1), (1, 2)]]
            for (l2, n2) in destinations:
                if (l1, n1) != (l2, n2) and l2 in range(8) and n2 in range(8):
                    move = letters[l1] + numbers[n1] + letters[l2] + numbers[n2]
                    labels_array.append(move)
    for l1 in range(8):
        l = letters[l1]
        for p in promoted_to:
            labels_array.append(l + '2' + l + '1' + p)
            labels_array.append(l + '7' + l + '8' + p)
            if l1 > 0:
                l_l = letters[l1 - 1]
                labels_array.append(l + '2' + l_l + '1' + p)
                labels_array.append(l + '7' + l_l + '8' + p)
            if l1 < 7:
                l_r = letters[l1 + 1]
                labels_array.append(l + '2' + l_r + '1' + p)
                labels_array.append(l + '7' + l_r + '8' + p)

    if include_drops:
        # Allowed drops
        for l in letters:
            for i, n in enumerate(numbers):
                for p in ('Q', 'R', 'B', 'N'):
                    labels_array.append(f'{p}@{l}{n}')
                if i > 0 and i < 7:
                    # Pawns cannot be dropped on 1st or 8th rank
                    labels_array.append(f'P@{l}{n}')
        
    return labels_array


# create layers for pieces in order = 'KQRBNPkqrbnp'  # 12x8x8
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


# Create layers for
# castling_order = 'KQkq'     # 4x8x8
# fifty-move-rule             # 1x8x8
# en en_passant               # 1x8x8
def aux_planes(board, add_promoted=False):

    fen = board.fen()

    foo = fen.split(' ')

    if add_promoted:
        promoted = bitboard_to_array(board.promoted)

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
                        en_passant]

    if add_promoted:
        auxiliary_planes.append(promoted)

    ret = np.asarray(auxiliary_planes, dtype=np.float32)
    if add_promoted:
        assert ret.shape == (7, 8, 8)
    else:
        assert ret.shape == (6, 8, 8)
    
    return ret


def alg_to_coord(alg):
    rank = 8 - int(alg[1])  # 0-7
    file = ord(alg[0]) - ord('a')  # 0-7
    return rank, file

def swap_uci_label(move: str):
    return ''.join([str(9-int(x)) if x.isdigit() else x for x in move])

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