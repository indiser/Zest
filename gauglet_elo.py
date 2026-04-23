import chess
import importlib
import multiprocessing
import math

# ==========================================
# CONFIGURATION
# ==========================================
BOT_A = "zest5"
BOT_B = "zest4"
GAMES = 200
TIME_LIMIT = 2.0  # Strict per-move time limit (seconds)
MAX_MOVES = 300   # Cap to prevent infinite games

# ==========================================
# BOT RUNNER
# ==========================================

def worker(bot_name, fen, queue):
    try:
        module = importlib.import_module(bot_name)
        move = module.next_move(fen)
        queue.put(move)
    except Exception as e:
        queue.put(None)

def get_move(bot_name, fen):
    queue = multiprocessing.Queue()
    p = multiprocessing.Process(target=worker, args=(bot_name, fen, queue))
    p.start()
    p.join(TIME_LIMIT + 1.0)
    if p.is_alive():
        p.terminate()
        return None
    return queue.get() if not queue.empty() else None

# ==========================================
# GAME ENGINE
# ==========================================

def play_game(white, black, game_number):
    board = chess.Board()
    moves = 0

    while not board.is_game_over() and moves < MAX_MOVES:
        bot = white if board.turn == chess.WHITE else black
        move_uci = get_move(bot, board.fen())

        if move_uci is None:
            loser = "White" if board.turn == chess.WHITE else "Black"
            result = (0, 1) if board.turn == chess.WHITE else (1, 0)
            reason = f"TIMEOUT ({loser})"
            return result, reason

        try:
            move = chess.Move.from_uci(move_uci)
        except ValueError:
            loser = "White" if board.turn == chess.WHITE else "Black"
            result = (0, 1) if board.turn == chess.WHITE else (1, 0)
            reason = f"ILLEGAL MOVE FORMAT ({loser})"
            return result, reason

        if move not in board.legal_moves:
            loser = "White" if board.turn == chess.WHITE else "Black"
            result = (0, 1) if board.turn == chess.WHITE else (1, 0)
            reason = f"ILLEGAL MOVE ({loser})"
            return result, reason

        board.push(move)
        moves += 1

    # Determine outcome
    if board.is_checkmate():
        winner = "Black" if board.turn == chess.WHITE else "White"
        return ((0, 1) if board.turn == chess.WHITE else (1, 0)), f"CHECKMATE ({winner} wins)"

    if board.is_stalemate():
        return (0.5, 0.5), "DRAW (Stalemate)"

    if board.is_insufficient_material():
        return (0.5, 0.5), "DRAW (Insufficient Material)"

    if board.is_seventyfive_moves():
        return (0.5, 0.5), "DRAW (75-Move Rule)"

    if board.is_fivefold_repetition():
        return (0.5, 0.5), "DRAW (Fivefold Repetition)"

    # Catch remaining draws via can_claim methods
    if board.can_claim_fifty_moves():
        return (0.5, 0.5), "DRAW (50-Move Rule)"

    if board.can_claim_threefold_repetition():
        return (0.5, 0.5), "DRAW (Threefold Repetition)"

    if moves >= MAX_MOVES:
        return (0.5, 0.5), f"DRAW (Move Limit: {MAX_MOVES} moves)"

    return (0.5, 0.5), "DRAW (Unknown)"

# ==========================================
# ELO CALCULATOR
# ==========================================

def calculate_elo(wins, losses, draws):
    total_games = wins + losses + draws
    if total_games == 0:
        print("No games played.")
        return

    score = wins + (draws * 0.5)
    expected_score = score / total_games

    print("\n" + "=" * 50)
    print("         TACTICAL ELO REPORT")
    print("=" * 50)
    print(f"  Total Games   : {total_games}")
    print(f"  {BOT_A} Wins  : {wins}")
    print(f"  {BOT_B} Wins  : {losses}")
    print(f"  Draws         : {draws}")
    print(f"  Win Rate (A)  : {expected_score * 100:.2f}%")

    if expected_score == 1.0:
        print(f"\n  ELO Difference: +400 (theoretical max — {BOT_A} won 100%)")
        print("=" * 50)
        return
    elif expected_score == 0.0:
        print(f"\n  ELO Difference: -400 (theoretical max — {BOT_B} won 100%)")
        print("=" * 50)
        return

    elo_diff = -400 * math.log10((1 / expected_score) - 1)

    variance = (
        wins   * (1.0 - expected_score) ** 2 +
        losses * (0.0 - expected_score) ** 2 +
        draws  * (0.5 - expected_score) ** 2
    ) / total_games

    std_dev = math.sqrt(variance)
    error_margin_score = 1.96 * (std_dev / math.sqrt(total_games))
    error_margin_elo = (400 / math.log(10)) * (
        error_margin_score / (expected_score * (1 - expected_score))
    )

    sign = "+" if elo_diff > 0 else ""
    print(f"  ELO Difference: {sign}{elo_diff:.1f} +/- {error_margin_elo:.1f} (95% CI)")
    print("=" * 50)

    if elo_diff - error_margin_elo > 0:
        print(f"\n  VERDICT: {BOT_A} is definitively stronger.")
        print(f"  The improvement is statistically significant.")
    elif elo_diff + error_margin_elo < 0:
        print(f"\n  VERDICT: {BOT_B} is definitively stronger.")
        print(f"  The improvement is statistically significant.")
    else:
        print(f"\n  VERDICT: INCONCLUSIVE.")
        print(f"  ELO gap is buried inside the margin of error.")
        print(f"  Play more games or the bots are near-equal strength.")

    print("=" * 50 + "\n")

# ==========================================
# TOURNAMENT RUNNER
# ==========================================

def run_tournament():
    wins_A, wins_B, draws = 0, 0, 0
    draw_reasons = {}

    print("=" * 50)
    print(f"  GAUNTLET: {BOT_A} vs {BOT_B}")
    print(f"  {GAMES} games | {TIME_LIMIT}s/move limit")
    print("=" * 50)

    for i in range(GAMES):
        # Alternate colors each game for fairness
        if i % 2 == 0:
            white, black = BOT_A, BOT_B
        else:
            white, black = BOT_B, BOT_A

        (res_w, res_b), reason = play_game(white, black, i + 1)

        # Map result back to A/B regardless of color
        if white == BOT_A:
            score_a, score_b = res_w, res_b
        else:
            score_a, score_b = res_b, res_w

        if score_a == 1:
            wins_A += 1
        elif score_b == 1:
            wins_B += 1
        else:
            draws += 1
            draw_reasons[reason] = draw_reasons.get(reason, 0) + 1

        color_a = "White" if white == BOT_A else "Black"
        print(
            f"  Game {i+1:>3}/{GAMES} | {BOT_A}={color_a} | "
            f"{reason:<35} | "
            f"Score -> A:{wins_A} B:{wins_B} D:{draws}"
        )

    # Draw breakdown
    if draw_reasons:
        print("\n  --- Draw Breakdown ---")
        for reason, count in sorted(draw_reasons.items(), key=lambda x: -x[1]):
            print(f"  {reason}: {count}")

    # Final ELO report
    calculate_elo(wins_A, wins_B, draws)


if __name__ == "__main__":
    multiprocessing.freeze_support()
    run_tournament()