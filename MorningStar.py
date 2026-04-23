import chess
import math
import time
import random
import chess.polyglot

piece_value = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

EXACT = 0
LOWERBOUND = 1
UPPERBOUND = 2

TT_MAX_SIZE = 1_000_000
TRANSPOSITION_TABLE = {}

killer_moves = [[None, None] for _ in range(100)]
history_table = [[0] * 64 for _ in range(64)]

OPENING_BOOK = {
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR": ["e2e4", "d2d4", "c2c4", "g1f3"],
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR": ["g1f3", "f2f4", "b1c3", "d2d3"],
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR": ["g1f3", "b1c3", "d2d4", "c2c3"],
    "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR": ["d2d4", "g1f3"],
    "rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR": ["d2d4", "b1c3"],
    "rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR": ["c2c4", "g1f3", "c1f4", "e2e3"],
    "rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR": ["c2c4", "g1f3", "c1g5"],
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR": ["e7e5", "c7c5", "e7e6", "c7c6"],
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R": ["b8c6", "g8f6", "d7d6"],
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R": ["d7d6", "b8c6", "e7e6"],
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR": ["d7d5", "g8f6"],
    "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR": ["e7e6", "c7c6", "d5c4"],
    "rnbqkb1r/pppppppp/5n2/8/2PP4/8/PP2PPPP/RNBQKBNR": ["e7e6", "g7g6"],
}

king_pst = [
     20, 30, 10,  0,  0, 10, 30, 20,
     20, 20,  0,  0,  0,  0, 20, 20,
    -10,-20,-20,-20,-20,-20,-20,-10,
    -20,-30,-30,-40,-40,-30,-30,-20,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30,
    -30,-40,-40,-50,-50,-40,-40,-30
]

king_endgame_pst = [
    -50,-40,-30,-20,-20,-30,-40,-50,
    -30,-20,-10,  0,  0,-10,-20,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 30, 40, 40, 30,-10,-30,
    -30,-10, 20, 30, 30, 20,-10,-30,
    -30,-30,  0,  0,  0,  0,-30,-30,
    -50,-30,-30,-30,-30,-30,-30,-50
]

knight_pst = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50,
]

pawn_pst = [
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10,-20,-20, 10, 10,  5,
     5, -5,-10,  0,  0,-10, -5,  5,
     0,  0,  0, 20, 20,  0,  0,  0,
     5,  5, 10, 25, 25, 10,  5,  5,
    10, 10, 20, 30, 30, 20, 10, 10,
    50, 50, 50, 50, 50, 50, 50, 50,
     0,  0,  0,  0,  0,  0,  0,  0
]

bishop_pst = [
    -20,-10,-10,-10,-10,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5, 10, 10,  5,  0,-10,
    -10,  5,  5, 10, 10,  5,  5,-10,
    -10,  0, 10, 10, 10, 10,  0,-10,
    -10, 10, 10, 10, 10, 10, 10,-10,
    -10,  5,  0,  0,  0,  0,  5,-10,
    -20,-10,-10,-10,-10,-10,-10,-20,
]

rook_pst = [
     0,  0,  5, 10, 10,  5,  0,  0,
    -5,  0,  5, 10, 10,  5,  0, -5,
    -5,  0,  5, 10, 10,  5,  0, -5,
    -5,  0,  5, 10, 10,  5,  0, -5,
    -5,  0,  5, 10, 10,  5,  0, -5,
    -5,  0,  5, 10, 10,  5,  0, -5,
     5, 10, 15, 20, 20, 15, 10,  5,
     0,  0,  5, 10, 10,  5,  0,  0
]

queen_pst = [
    -20,-10,-10, -5, -5,-10,-10,-20,
    -10,  0,  0,  0,  0,  0,  0,-10,
    -10,  0,  5,  5,  5,  5,  0,-10,
     -5,  0,  5,  5,  5,  5,  0, -5,
      0,  0,  5,  5,  5,  5,  0, -5,
    -10,  5,  5,  5,  5,  5,  0,-10,
    -10,  0,  5,  0,  0,  0,  0,-10,
    -20,-10,-10, -5, -5,-10,-10,-20
]


class SearchTimeout(Exception):
    pass


# ---------------- PAWN STRUCTURE HELPERS ---------------- #

def _pawn_file_masks():
    """Precompute: for each file 0-7, set of squares on that file."""
    return [
        {chess.square(f, r) for r in range(8)}
        for f in range(8)
    ]

PAWN_FILE_SQUARES = _pawn_file_masks()

def pawn_structure_score(board, color):
    """
    Returns a score (positive = good for `color`) evaluating:
      - Passed pawns: big bonus scaled by how advanced the pawn is
      - Doubled pawns: penalty per extra pawn on same file
      - Isolated pawns: penalty if no friendly pawns on adjacent files
    """
    score = 0
    enemy = not color
    own_pawns = list(board.pieces(chess.PAWN, color))
    enemy_pawns = set(board.pieces(chess.PAWN, enemy))

    # Group own pawns by file
    pawns_on_file = {}
    for sq in own_pawns:
        f = chess.square_file(sq)
        pawns_on_file.setdefault(f, []).append(sq)

    for f, squares in pawns_on_file.items():
        # --- Doubled pawn penalty ---
        if len(squares) > 1:
            score -= 20 * (len(squares) - 1)

        # --- Isolated pawn penalty ---
        has_neighbor = any(
            nf in pawns_on_file
            for nf in [f - 1, f + 1]
            if 0 <= nf <= 7
        )
        if not has_neighbor:
            score -= 15 * len(squares)

        # --- Passed pawn bonus per pawn on this file ---
        for sq in squares:
            rank = chess.square_rank(sq) if color == chess.WHITE else 7 - chess.square_rank(sq)

            # A pawn is passed if no enemy pawns can ever block or capture it
            is_passed = True
            for ef in [f - 1, f, f + 1]:
                if not (0 <= ef <= 7):
                    continue
                for er in range(8):
                    esq = chess.square(ef, er)
                    if esq not in enemy_pawns:
                        continue
                    er_normalized = er if color == chess.BLACK else 7 - er
                    # Enemy pawn is "ahead" of ours if it's further advanced
                    if er_normalized > rank:
                        is_passed = False
                        break
                if not is_passed:
                    break

            if is_passed:
                # Bonus scales aggressively with advancement
                passed_bonuses = [0, 10, 20, 40, 70, 120, 200, 0]
                score += passed_bonuses[min(rank, 7)]

                # Extra bonus if the path to promotion is clear
                clear_path = True
                for advance_rank in range(rank + 1, 7):
                    ar = advance_rank if color == chess.WHITE else 7 - advance_rank
                    path_sq = chess.square(f, ar)
                    if board.piece_at(path_sq):
                        clear_path = False
                        break
                if clear_path:
                    score += passed_bonuses[min(rank, 7)] // 2

    return score


def rook_open_file_score(board, color):
    """Bonus for rooks on open or semi-open files."""
    score = 0
    enemy = not color
    for sq in board.pieces(chess.ROOK, color):
        f = chess.square_file(sq)
        own_pawns_on_file = any(
            board.piece_at(chess.square(f, r)) == chess.Piece(chess.PAWN, color)
            for r in range(8)
        )
        enemy_pawns_on_file = any(
            board.piece_at(chess.square(f, r)) == chess.Piece(chess.PAWN, enemy)
            for r in range(8)
        )
        if not own_pawns_on_file and not enemy_pawns_on_file:
            score += 30   # fully open file
        elif not own_pawns_on_file:
            score += 15   # semi-open file (only enemy pawn)
    return score


def bishop_pair_bonus(board, color):
    """Two bishops is worth ~30cp bonus in open positions."""
    if len(list(board.pieces(chess.BISHOP, color))) >= 2:
        return 30
    return 0


def king_safety_score(board, color, is_endgame):
    """
    Evaluates king safety by checking:
    - Pawn shield presence and quality
    - Open/semi-open files near the king (attack vectors)
    Returns score from `color`'s perspective (positive = safe).
    """
    if is_endgame:
        return 0

    king_sq = board.king(color)
    king_file = chess.square_file(king_sq)
    king_rank = chess.square_rank(king_sq)
    score = 0

    # Pawn shield: one rank ahead, three files wide
    shield_rank = king_rank + 1 if color == chess.WHITE else king_rank - 1
    if 0 <= shield_rank <= 7:
        for f in range(max(0, king_file - 1), min(7, king_file + 1) + 1):
            shield_sq = chess.square(f, shield_rank)
            piece = board.piece_at(shield_sq)
            if piece and piece.piece_type == chess.PAWN and piece.color == color:
                score += 15   # shield pawn in place
            else:
                # Check if pawn is one further rank back (slightly pushed shield)
                shield_rank2 = shield_rank + (1 if color == chess.WHITE else -1)
                if 0 <= shield_rank2 <= 7:
                    piece2 = board.piece_at(chess.square(f, shield_rank2))
                    if piece2 and piece2.piece_type == chess.PAWN and piece2.color == color:
                        score -= 5   # pawn pushed — weaker shield but not gone
                    else:
                        score -= 25  # no shield pawn at all

    # Open file penalty: enemy can slide into the king
    for f in range(max(0, king_file - 1), min(7, king_file + 1) + 1):
        own_pawn_on_file = any(
            board.piece_at(chess.square(f, r)) == chess.Piece(chess.PAWN, color)
            for r in range(8)
        )
        enemy_pawn_on_file = any(
            board.piece_at(chess.square(f, r)) == chess.Piece(chess.PAWN, not color)
            for r in range(8)
        )
        if not own_pawn_on_file:
            score -= 15   # semi-open: enemy can attack along this file
        if not own_pawn_on_file and not enemy_pawn_on_file:
            score -= 15   # fully open: even worse (rook/queen can slide through)

    # Attacker proximity: count enemy pieces near the king
    enemy = not color
    attack_weight = {
        chess.QUEEN: 4,
        chess.ROOK: 2,
        chess.BISHOP: 1,
        chess.KNIGHT: 1,
    }
    attack_score = 0
    attack_count = 0
    king_zone = chess.SquareSet(chess.BB_KING_ATTACKS[king_sq])
    for piece_type, weight in attack_weight.items():
        for piece_sq in board.pieces(piece_type, enemy):
            attacks = board.attacks(piece_sq)
            overlap = len(attacks & king_zone)
            if overlap:
                attack_score += weight * overlap
                attack_count += 1

    # Scale danger non-linearly: many attackers = exponentially more dangerous
    danger_table = [0, 0, 1, 2, 4, 8, 14, 20, 28, 36]
    danger_idx = min(attack_count, len(danger_table) - 1)
    score -= attack_score * danger_table[danger_idx]

    return score


# ---------------- EVALUATION ---------------- #

def evaluate(board):
    if board.is_checkmate():
        return -99999 if board.turn == chess.WHITE else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    if board.can_claim_threefold_repetition() or board.can_claim_fifty_moves():
        return 50 if board.turn == chess.WHITE else -50

    score = 0
    total_pieces = len(board.piece_map())
    has_queens = bool(board.pieces(chess.QUEEN, chess.WHITE) or board.pieces(chess.QUEEN, chess.BLACK))
    is_endgame = (not has_queens and total_pieces <= 14) or total_pieces <= 6

    # --- Material + PST ---
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if not piece:
            continue
        value = piece_value[piece.piece_type] * 100
        pst_index = square if piece.color == chess.WHITE else chess.square_mirror(square)

        if piece.piece_type == chess.KNIGHT:
            value += knight_pst[pst_index]
        elif piece.piece_type == chess.PAWN:
            value += pawn_pst[pst_index]
        elif piece.piece_type == chess.BISHOP:
            value += bishop_pst[pst_index]
        elif piece.piece_type == chess.ROOK:
            if not is_endgame:
                value += rook_pst[pst_index]
            else:
                enemy_king_sq = board.king(not piece.color)
                if (chess.square_rank(square) == chess.square_rank(enemy_king_sq) or
                        chess.square_file(square) == chess.square_file(enemy_king_sq)):
                    value += 30
        elif piece.piece_type == chess.QUEEN:
            if not is_endgame:
                value += queen_pst[pst_index]
        elif piece.piece_type == chess.KING:
            value += king_endgame_pst[pst_index] if is_endgame else king_pst[pst_index]

        score += value if piece.color == chess.WHITE else -value

    # --- Pawn structure (passed, doubled, isolated) ---
    score += pawn_structure_score(board, chess.WHITE)
    score -= pawn_structure_score(board, chess.BLACK)

    # --- Rook open file bonuses ---
    score += rook_open_file_score(board, chess.WHITE)
    score -= rook_open_file_score(board, chess.BLACK)

    # --- Bishop pair ---
    score += bishop_pair_bonus(board, chess.WHITE)
    score -= bishop_pair_bonus(board, chess.BLACK)

    # --- King safety ---
    score += king_safety_score(board, chess.WHITE, is_endgame)
    score -= king_safety_score(board, chess.BLACK, is_endgame)

    # --- Mobility (both sides, turn-independent) ---
    own_mobility = board.legal_moves.count()
    board.push(chess.Move.null())
    enemy_mobility = board.legal_moves.count() if not board.is_check() else 0
    board.pop()
    mobility_weight = 3.0 if is_endgame else 0.1
    mobility_diff = own_mobility - enemy_mobility
    score += mobility_diff * mobility_weight * (1 if board.turn == chess.WHITE else -1)

    # --- Mop-up: push losing king to edge and approach with winning king ---
    if abs(score) > 100:
        winning_color = chess.WHITE if score > 0 else chess.BLACK
        losing_color = not winning_color
        losing_king_sq = board.king(losing_color)
        losing_rank = chess.square_rank(losing_king_sq)
        losing_file = chess.square_file(losing_king_sq)
        center_distance = abs(losing_rank - 3.5) + abs(losing_file - 3.5)
        mop_up_bonus = center_distance * 20
        if not has_queens and total_pieces <= 10:
            winning_king_sq = board.king(winning_color)
            distance_between_kings = (
                abs(losing_rank - chess.square_rank(winning_king_sq)) +
                abs(losing_file - chess.square_file(winning_king_sq))
            )
            mop_up_bonus += (14 - distance_between_kings) * 10
        score += mop_up_bonus if winning_color == chess.WHITE else -mop_up_bonus

    # --- Tempo/conversion: penalize shuffling when winning ---
    if abs(score) > 100:
        score -= board.halfmove_clock * (1 if score > 0 else -1)

    # --- Piece activity scaling: amplify advantage as pieces come off ---
    if score > 50:
        score += (32 - total_pieces) * 10
    elif score < -50:
        score -= (32 - total_pieces) * 10

    return score


def order_moves(board, moves, depth=0, tt_move=None):
    def guess_move_score(move):
        if move == tt_move:
            return 20000
        if board.is_capture(move):
            attacker = board.piece_at(move.from_square)
            victim = board.piece_at(move.to_square)
            if victim and attacker:
                return 10000 + (10 * piece_value[victim.piece_type] - piece_value[attacker.piece_type])
            return 10000
        if move.promotion:
            return 9000 + piece_value[move.promotion] * 10
        if board.gives_check(move):
            return 8000
        if depth < len(killer_moves) and move in killer_moves[depth]:
            return 5000
        return history_table[move.from_square][move.to_square]
    return sorted(moves, key=guess_move_score, reverse=True)


def quiescence(board, alpha, beta, maximizing, start_time, time_limit, qdepth=0):
    if time.time() - start_time > time_limit:
        raise SearchTimeout()

    eval_score = evaluate(board)

    if maximizing:
        if eval_score >= beta:
            return eval_score
        alpha = max(alpha, eval_score)
    else:
        if eval_score <= alpha:
            return eval_score
        beta = min(beta, eval_score)

    tactical_moves = []
    for move in board.legal_moves:
        if board.is_capture(move) or move.promotion:
            tactical_moves.append(move)
        elif qdepth < 2 and board.gives_check(move):
            tactical_moves.append(move)

    if maximizing:
        max_eval = eval_score
        for move in order_moves(board, tactical_moves):
            board.push(move)
            score = quiescence(board, alpha, beta, False, start_time, time_limit, qdepth + 1)
            board.pop()
            max_eval = max(max_eval, score)
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = eval_score
        for move in order_moves(board, tactical_moves):
            board.push(move)
            score = quiescence(board, alpha, beta, True, start_time, time_limit, qdepth + 1)
            board.pop()
            min_eval = min(min_eval, score)
            beta = min(beta, score)
            if beta <= alpha:
                break
        return min_eval


def lmr_reduction(depth, move_number):
    if depth >= 3 and move_number >= 4:
        return max(1, int(0.5 + math.log(depth) * math.log(move_number) / 2.5))
    return 0


def minimax(board, depth, alpha, beta, maximizing, start_time, time_limit, null_allowed=True):
    if time.time() - start_time > time_limit:
        raise SearchTimeout()

    alpha_orig = alpha
    board_hash = chess.polyglot.zobrist_hash(board)
    tt_move = None

    if board_hash in TRANSPOSITION_TABLE:
        tt_entry = TRANSPOSITION_TABLE[board_hash]
        tt_move = tt_entry.get('best_move')
        if tt_entry['depth'] >= depth:
            if tt_entry['flag'] == EXACT:
                return tt_entry['score']
            elif tt_entry['flag'] == LOWERBOUND:
                alpha = max(alpha, tt_entry['score'])
            elif tt_entry['flag'] == UPPERBOUND:
                beta = min(beta, tt_entry['score'])
            if alpha >= beta:
                return tt_entry['score']

    if board.can_claim_threefold_repetition():
        return 50 if board.turn == chess.WHITE else -50

    if depth <= 0:
        if not board.is_check() or depth < -3:
            return quiescence(board, alpha, beta, maximizing, start_time, time_limit)

    if board.is_game_over():
        return evaluate(board)

    in_check = board.is_check()
    non_pawn_pieces = len(board.piece_map()) - len(list(board.pieces(chess.PAWN, board.turn))) - 1
    if null_allowed and not in_check and depth >= 3 and non_pawn_pieces > 2:
        R = 3 if depth >= 6 else 2
        board.push(chess.Move.null())
        null_score = minimax(board, depth - 1 - R, alpha, beta, not maximizing,
                             start_time, time_limit, null_allowed=False)
        board.pop()
        if maximizing and null_score >= beta:
            return beta
        if not maximizing and null_score <= alpha:
            return alpha

    best_move = None
    moves = order_moves(board, list(board.legal_moves), depth, tt_move)

    if maximizing:
        max_eval = -math.inf
        for move_number, move in enumerate(moves):
            board.push(move)
            is_quiet = (not board.is_capture(move) and not move.promotion and not board.is_check())
            reduction = lmr_reduction(depth, move_number) if is_quiet else 0
            if reduction > 0:
                eval_score = minimax(board, depth - 1 - reduction, alpha, beta, False, start_time, time_limit)
                if eval_score > alpha:
                    eval_score = minimax(board, depth - 1, alpha, beta, False, start_time, time_limit)
            else:
                eval_score = minimax(board, depth - 1, alpha, beta, False, start_time, time_limit)
            board.pop()
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                if not board.is_capture(move):
                    if depth < len(killer_moves):
                        if killer_moves[depth][0] != move:
                            killer_moves[depth][1] = killer_moves[depth][0]
                            killer_moves[depth][0] = move
                    history_table[move.from_square][move.to_square] += depth * depth
                break
        best_score = max_eval
    else:
        min_eval = math.inf
        for move_number, move in enumerate(moves):
            board.push(move)
            is_quiet = (not board.is_capture(move) and not move.promotion and not board.is_check())
            reduction = lmr_reduction(depth, move_number) if is_quiet else 0
            if reduction > 0:
                eval_score = minimax(board, depth - 1 - reduction, alpha, beta, True, start_time, time_limit)
                if eval_score < beta:
                    eval_score = minimax(board, depth - 1, alpha, beta, True, start_time, time_limit)
            else:
                eval_score = minimax(board, depth - 1, alpha, beta, True, start_time, time_limit)
            board.pop()
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
            beta = min(beta, eval_score)
            if beta <= alpha:
                if not board.is_capture(move):
                    if depth < len(killer_moves):
                        if killer_moves[depth][0] != move:
                            killer_moves[depth][1] = killer_moves[depth][0]
                            killer_moves[depth][0] = move
                    history_table[move.from_square][move.to_square] += depth * depth
                break
        best_score = min_eval

    if len(TRANSPOSITION_TABLE) >= TT_MAX_SIZE:
        TRANSPOSITION_TABLE.pop(next(iter(TRANSPOSITION_TABLE)))

    flag = UPPERBOUND if best_score <= alpha_orig else (LOWERBOUND if best_score >= beta else EXACT)
    TRANSPOSITION_TABLE[board_hash] = {
        'score': best_score,
        'depth': depth,
        'flag': flag,
        'best_move': best_move
    }
    return best_score


def next_move(fen):
    global history_table, killer_moves

    board = chess.Board(fen)

    for move in board.legal_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return str(move)
        board.pop()

    random.seed(int(time.time() * 1000) + hash(fen))
    current_position = board.board_fen()
    if current_position in OPENING_BOOK:
        possible_book_moves = OPENING_BOOK[current_position]
        chosen = random.choice(possible_book_moves)
        book_move = chess.Move.from_uci(chosen)
        if book_move in board.legal_moves:
            return str(book_move)

    for i in range(64):
        for j in range(64):
            history_table[i][j] //= 2

    killer_moves = [[None, None] for _ in range(100)]

    start_time = time.time()
    time_limit = 3.5
    is_white = board.turn == chess.WHITE

    best_move_overall = list(board.legal_moves)[0]
    prev_score = 0
    ASPIRATION_WINDOW = 50

    for depth in range(1, 12):
        try:
            if depth >= 3:
                alpha = prev_score - ASPIRATION_WINDOW
                beta  = prev_score + ASPIRATION_WINDOW
            else:
                alpha = -math.inf
                beta  = math.inf

            while True:
                best_score = -math.inf if is_white else math.inf
                current_depth_best_move = None

                for move in order_moves(board, list(board.legal_moves), depth):
                    board.push(move)
                    score = minimax(board, depth - 1, alpha, beta, not is_white, start_time, time_limit)
                    board.pop()

                    if is_white and score > 90000:
                        return str(move)
                    elif not is_white and score < -90000:
                        return str(move)

                    if is_white:
                        if score > best_score:
                            best_score = score
                            current_depth_best_move = move
                        alpha = max(alpha, score)
                    else:
                        if score < best_score:
                            best_score = score
                            current_depth_best_move = move
                        beta = min(beta, score)

                if depth >= 3:
                    if best_score <= prev_score - ASPIRATION_WINDOW:
                        alpha = -math.inf
                        continue
                    elif best_score >= prev_score + ASPIRATION_WINDOW:
                        beta = math.inf
                        continue
                break

            if current_depth_best_move:
                best_move_overall = current_depth_best_move
                prev_score = best_score

        except SearchTimeout:
            break

    return str(best_move_overall)