
import chess
from deepChess import ChessUtils

MAX_SCORE=1000
MIN_SCORE=-1000

def alpha_beta_result(game_state : ChessUtils.MyChessEnv, max_depth,
                      best_black, best_white, eval_fn):
    if game_state.done():
        if game_state.winner() == game_state.next_player:
            return MAX_SCORE
        else:
            return MIN_SCORE

    if max_depth == 0:
        return eval_fn(game_state)

    best_so_far = MIN_SCORE
    for candidate_move in game_state.legal_moves():
        next_state = game_state.apply_move(candidate_move)
        opponent_best_result = alpha_beta_result(
            next_state, max_depth - 1,
            best_black, best_white,
            eval_fn)
        our_result = -1 * opponent_best_result

        if our_result > best_so_far:
            best_so_far = our_result
        if game_state.next_player == chess.WHITE:
            if best_so_far > best_white:
                best_white = best_so_far
            outcome_for_black = -1 * best_so_far
            if outcome_for_black < best_black:
                return best_so_far
        elif game_state.next_player == chess.BLACK:
            if best_so_far > best_black:
                best_black = best_so_far
            outcome_for_white = -1 * best_so_far
            if outcome_for_white < best_white:
                return best_so_far

    return best_so_far


def minimax(depth, env:ChessUtils.MyChessEnv, alpha, beta, is_maximizing):
    if(depth == 0):
        return -ChessUtils.position_evaluation_simple(env.observation())
    possibleMoves = env.possible_moves()
    if(is_maximizing):
        bestMove =MIN_SCORE
        for x in possibleMoves:
            move = chess.Move.from_uci(str(x))
            env.step(move)
            bestMove = max(bestMove,minimax(depth - 1, env , alpha,beta, not is_maximizing))
            env.undo()
            alpha = max(alpha, bestMove)
            if beta <= alpha:
                return bestMove
        return bestMove
    else:
        bestMove = MAX_SCORE
        for x in possibleMoves:
            move = chess.Move.from_uci(str(x))
            env.step(move)
            bestMove = min(bestMove, minimax(depth - 1, env,alpha,beta, not is_maximizing))
            env.undo()
            beta = min(beta,bestMove)
            if(beta <= alpha):
                return bestMove
        return bestMove