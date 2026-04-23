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
TRANSPOSITION_TABLE = {}
killer_moves = [[None, None] for _ in range(100)] # Tracks 2 killer moves per depth
history_table = [[0] * 64 for _ in range(64)]

# ---------------- OPENING BOOK ---------------- #
# Maps a board state (FEN without counters) to a specific UCI move.
# This forces the bot to play standard center-control openings.

# ---------------- OPENING BOOK ---------------- #
# OPENING_BOOK = {
#     # --- WHITE: e4 Openings ---
#     "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR": "e2e4", # Move 1
#     "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR": "g1f3", # e4 e5 -> Nf3
#     "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R": "f1c4", # Italian Game
#     "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R": "e1g1", # Castle in Italian
    
#     # --- WHITE: Against the Sicilian (c5) ---
#     "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR": "g1f3", # e4 c5 -> Nf3
#     "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R": "d2d4", # Open Sicilian
#     "rnbqkbnr/pp2pppp/3p4/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R": "d2d4", # Open Sicilian

#     # --- WHITE: Against the French (e6) ---
#     "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR": "d2d4", # e4 e6 -> d4
#     "rnbqkbnr/pppp1ppp/4p3/8/3PP3/8/PPP2PPP/RNBQKBNR": "b1c3", # e4 e6 d4 d5 -> Nc3

#     # --- BLACK: Defending against e4 ---
#     "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR": "e7e5", # Respond to e4 with e5
#     "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R": "b8c6", # Defend pawn with Nc6
#     "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R": "g8f6", # Two Knights Defense
#     "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R": "a7a6", # Ruy Lopez -> a6

#     # --- BLACK: Defending against d4 ---
#     "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR": "d7d5", # Respond to d4 with d5
#     "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR": "e7e6", # Queen's Gambit Declined
#     "rnbqkbnr/ppp1pppp/8/3p4/3P4/5N2/PPP1PPPP/RNBQKB1R": "g8f6", # Develop Knight
# }

# OPENING_BOOK = {
#     # --- WHITE: Move 1 (The Four Majors) ---
#     "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR": ["e2e4", "d2d4", "c2c4", "g1f3"], 
    
#     # --- WHITE: e4 Follow-ups ---
#     "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR": ["g1f3", "f2f4", "b1c3"], # e4 e5 responses (Knight, King's Gambit, Vienna)
#     "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR": ["g1f3", "b1c3"], # Anti-Sicilian
#     "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR": ["d2d4"], # French Defense response
#     "rnbqkbnr/pp1ppppp/2p5/4P3/8/PPPP1PPP/RNBQKBNR": ["d2d4"], # Caro-Kann response

#     # --- WHITE: d4 Follow-ups ---
#     "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR": ["c2c4", "g1f3"], # Queen's Gambit or Indian setups

#     # --- BLACK: Defending against e4 ---
#     "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR": ["e7e5", "c7c5", "e7e6", "c7c6"], # e5, Sicilian, French, Caro-Kann
    
#     # --- BLACK: Defending against d4 ---
#     "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR": ["d7d5", "g8f6"], # d5 or King's Indian Defense
#     "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR": ["e7e6", "c7c6"], # QGD or Slav
# }

# ---------------- OPENING BOOK ---------------- #
OPENING_BOOK = {
    # ---------------- MOVE 1 ---------------- #
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR": ["e2e4", "d2d4", "c2c4", "g1f3"], 
    
    # ---------------- WHITE: Responses to 1. e4 ---------------- #
    # Black plays 1... e5
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR": ["g1f3", "f2f4", "b1c3", "d2d3"], 
    # Black plays 1... c5 (Sicilian)
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR": ["g1f3", "b1c3", "d2d4", "c2c3"], 
    # Black plays 1... e6 (French)
    "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR": ["d2d4", "g1f3"], 
    # Black plays 1... c6 (Caro-Kann)
    "rnbqkbnr/pp1ppppp/2p5/8/4P3/8/PPPP1PPP/RNBQKBNR": ["d2d4", "b1c3"], 

    # ---------------- WHITE: Responses to 1. d4 ---------------- #
    # Black plays 1... d5
    "rnbqkbnr/ppp1pppp/8/3p4/3P4/8/PPP1PPPP/RNBQKBNR": ["c2c4", "g1f3", "c1f4", "e2e3"], 
    # Black plays 1... Nf6
    "rnbqkb1r/pppppppp/5n2/8/3P4/8/PPP1PPPP/RNBQKBNR": ["c2c4", "g1f3", "c1g5"], 

    # ---------------- BLACK: Defenses against 1. e4 ---------------- #
    # White plays 1. e4
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR": ["e7e5", "c7c5", "e7e6", "c7c6"], 
    # White plays 1. e4, Black plays e5, White plays 2. Nf3
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R": ["b8c6", "g8f6", "d7d6"], 
    # White plays 1. e4, Black plays c5, White plays 2. Nf3
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R": ["d7d6", "b8c6", "e7e6"], 

    # ---------------- BLACK: Defenses against 1. d4 ---------------- #
    # White plays 1. d4
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR": ["d7d5", "g8f6"], 
    # White plays 1. d4, Black plays d5, White plays 2. c4
    "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR": ["e7e6", "c7c6", "d5c4"], 
    # White plays 1. d4, Black plays Nf6, White plays 2. c4
    "rnbqkb1r/pppppppp/5n2/8/2PP4/8/PP2PPPP/RNBQKBNR": ["e7e6", "g7g6"], 
}

king_pst = [
     20, 30, 10,  0,  0, 10, 30, 20, # Rank 1: Castling squares highly rewarded
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
     0,  0,  5, 10, 10,  5,  0,  0, # Rank 1: Heavy centralization on d1, e1
    -5,  0,  5, 10, 10,  5,  0, -5, # Rank 2: Push to open central files
    -5,  0,  5, 10, 10,  5,  0, -5, # Rank 3
    -5,  0,  5, 10, 10,  5,  0, -5, # Rank 4
    -5,  0,  5, 10, 10,  5,  0, -5, # Rank 5
    -5,  0,  5, 10, 10,  5,  0, -5, # Rank 6
     5, 10, 15, 20, 20, 15, 10,  5, # Rank 7: Absolute dominance and center control
     0,  0,  5, 10, 10,  5,  0,  0  # Rank 8
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

# ---------------- EVALUATION ---------------- #

def evaluate(board, depth=0):

    # checkmate = highest priority
    if board.is_checkmate():
        return (-99999 - depth) if board.turn else (99999 + depth)
    
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
    
    if board.can_claim_threefold_repetition() or board.can_claim_fifty_moves():
        return 50 if board.turn == chess.WHITE else -50
    
    
    score = 0
    total_pieces = len(board.piece_map())
    has_queens = bool(board.pieces(chess.QUEEN, chess.WHITE) or board.pieces(chess.QUEEN, chess.BLACK))
    # enemy_has_queens = bool(board.pieces(chess.QUEEN, losing_color))
    is_endgame = (not has_queens and total_pieces <= 14) or total_pieces <= 6
    # material
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = piece_value[piece.piece_type] * 100
            if piece.piece_type == chess.KNIGHT:
                # If Black, flip the board perspective
                pst_index = square if piece.color == chess.WHITE else chess.square_mirror(square)
                value += knight_pst[pst_index]
            elif piece.piece_type == chess.PAWN:
                pst_index = square if piece.color == chess.WHITE else chess.square_mirror(square)
                pawn_val = pawn_pst[pst_index]
                
                if is_endgame:
                    rank = chess.square_rank(square) if piece.color == chess.WHITE else 7 - chess.square_rank(square)
                    if rank == 3: pawn_val += 50   # 4th rank: starting the engine
                    if rank == 4: pawn_val += 150
                    if rank == 5: pawn_val += 200 # 6th rank is highly dangerous
                    if rank == 6: pawn_val += 500 # 7th rank is an absolute priority
                value += pawn_val
                # value += pawn_pst[pst_index]
            elif piece.piece_type == chess.BISHOP:
                pst_index = square if piece.color == chess.WHITE else chess.square_mirror(square)
                value += bishop_pst[pst_index]
            elif piece.piece_type == chess.ROOK:
                pst_index = square if piece.color == chess.WHITE else chess.square_mirror(square)
                value += rook_pst[pst_index] if not is_endgame else 0
                if is_endgame:
                    enemy_king_sq = board.king(not piece.color)
                    if chess.square_rank(square) == chess.square_rank(enemy_king_sq) or \
                       chess.square_file(square) == chess.square_file(enemy_king_sq):
                        value += 30
            elif piece.piece_type == chess.QUEEN:
                pst_index = square if piece.color == chess.WHITE else chess.square_mirror(square)
                value += queen_pst[pst_index] if not is_endgame else 0
            elif piece.piece_type == chess.KING:
                pst_index = square if piece.color == chess.WHITE else chess.square_mirror(square)
                value += king_endgame_pst[pst_index] if is_endgame else king_pst[pst_index]
            score += value if piece.color == chess.WHITE else -value
    
    if score > 50:
        score += (32 - total_pieces) * 10
    elif score < -50:
        score -= (32 - total_pieces) * 10
    
    if abs(score) > 100: 
        winning_color = chess.WHITE if score > 0 else chess.BLACK
        losing_color = not winning_color
        
        losing_king_sq = board.king(losing_color)
        
        # 1. ALWAYS push the losing king to the edge, no matter what.
        losing_rank = chess.square_rank(losing_king_sq)
        losing_file = chess.square_file(losing_king_sq)
        center_distance = abs(losing_rank - 3.5) + abs(losing_file - 3.5)
        mop_up_bonus = center_distance * 20
        
        # 2. STRICT GATE: ONLY march our King forward if BOTH Queens are dead AND it's a true endgame.
        has_queens = bool(board.pieces(chess.QUEEN, chess.WHITE) or board.pieces(chess.QUEEN, chess.BLACK))
        total_pieces = len(board.piece_map())
        
        if not has_queens and total_pieces <= 10:
            winning_king_sq = board.king(winning_color)
            winning_rank = chess.square_rank(winning_king_sq)
            winning_file = chess.square_file(winning_king_sq)
            distance_between_kings = abs(losing_rank - winning_rank) + abs(losing_file - winning_file)
            mop_up_bonus += (14 - distance_between_kings) * 10
            
        if winning_color == chess.WHITE:
            score += mop_up_bonus
        else:
            score -= mop_up_bonus

    if not is_endgame:
        # White King Safety
        wk_sq = board.king(chess.WHITE)
        if wk_sq in [chess.G1, chess.H1]: # Kingside Castled
            if not board.piece_at(chess.F2) and not board.piece_at(chess.F3): score -= 50
            if not board.piece_at(chess.G2) and not board.piece_at(chess.G3): score -= 50
            if not board.piece_at(chess.H2) and not board.piece_at(chess.H3): score -= 50
        elif wk_sq in [chess.C1, chess.B1, chess.A1]: # Queenside Castled
            if not board.piece_at(chess.A2) and not board.piece_at(chess.A3): score -= 50
            if not board.piece_at(chess.B2) and not board.piece_at(chess.B3): score -= 50
            if not board.piece_at(chess.C2) and not board.piece_at(chess.C3): score -= 50
            
        # Black King Safety
        bk_sq = board.king(chess.BLACK)
        if bk_sq in [chess.G8, chess.H8]: # Kingside Castled
            if not board.piece_at(chess.F7) and not board.piece_at(chess.F6): score += 50
            if not board.piece_at(chess.G7) and not board.piece_at(chess.G6): score += 50
            if not board.piece_at(chess.H7) and not board.piece_at(chess.H6): score += 50
        elif bk_sq in [chess.C8, chess.B8, chess.A8]: # Queenside Castled
            if not board.piece_at(chess.A7) and not board.piece_at(chess.A6): score += 50
            if not board.piece_at(chess.B7) and not board.piece_at(chess.B6): score += 50
            if not board.piece_at(chess.C7) and not board.piece_at(chess.C6): score += 50
            
    # check pressure (fixed logic)

    if board.is_check():
        if board.turn == chess.WHITE:
            score -= 2
        else:
            score += 2
    
    mobility = board.legal_moves.count()
    mobility_weight = 5.0 if is_endgame else 0.1

    if board.turn == chess.WHITE:
        score += mobility * mobility_weight
    else:
        score -= mobility * mobility_weight
    
    if score > 100:
        score -= board.halfmove_clock
    elif score < -100:
        score += board.halfmove_clock

    return score


# ---------------- MOVE ORDERING (TT + MVV-LVA + Checks + Heuristics) ---------------- #

def order_moves(board, moves, depth=0, tt_move=None):
    def guess_move_score(move):
        score = 0
        
        # 0. TRANSPOSITION TABLE MOVE (Absolute Highest Priority)
        if move == tt_move:
            return 20000
            
        # 1. MVV-LVA (Highest Priority: Captures)
        if board.is_capture(move):
            attacker = board.piece_at(move.from_square)
            victim = board.piece_at(move.to_square)
            if victim and attacker:
                score += 10000 + (10 * piece_value[victim.piece_type] - piece_value[attacker.piece_type])
            else:
                score += 10000 # En Passant
                
        # 2. Promotions
        elif move.promotion:
            score += 9000 + piece_value[move.promotion] * 10
            
        # 3. CHECKS 
        elif board.gives_check(move):
            score += 8000
            
        # 4. Killer Heuristic 
        elif move in killer_moves[depth]:
            score += 5000
            
        # 5. History Heuristic 
        else:
            score += history_table[move.from_square][move.to_square]
            
        return score
    
    return sorted(moves, key=guess_move_score, reverse=True)

# ---------------- QUIESCENCE SEARCH ---------------- #
def quiescence(board, alpha, beta, maximizing, start_time, time_limit):
    if time.time() - start_time > time_limit:
        raise SearchTimeout()
        
    eval_score = evaluate(board, 0)
    
    if maximizing:
        alpha = max(alpha, eval_score)
        if beta <= alpha:
            return eval_score
    else:
        beta = min(beta, eval_score)
        if beta <= alpha:
            return eval_score
            
    # Only search captures! This stops the Horizon Effect without exploding processing time.
    # captures = [move for move in board.legal_moves if board.is_capture(move)]
    tactical_moves = [move for move in board.legal_moves if board.is_capture(move) or move.promotion]
    
    if maximizing:
        max_eval = eval_score
        for move in order_moves(board, tactical_moves):
            board.push(move)
            score = quiescence(board, alpha, beta, False, start_time, time_limit)
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
            score = quiescence(board, alpha, beta, True, start_time, time_limit)
            board.pop()
            min_eval = min(min_eval, score)
            beta = min(beta, score)
            if beta <= alpha:
                break
        return min_eval
    

# ---------------- MINIMAX (With Transposition Table) ---------------- #

def minimax(board, depth, alpha, beta, maximizing, start_time, time_limit):
    if time.time() - start_time > time_limit:
        raise SearchTimeout()

    # --- 1. TT LOOKUP ---
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
        return evaluate(board, depth)

    best_move = None

    if maximizing:
        max_eval = -math.inf
        for move in order_moves(board, list(board.legal_moves), depth, tt_move):
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False, start_time, time_limit)
            board.pop()
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
                
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                if not board.is_capture(move):
                    if killer_moves[depth][0] != move:
                        killer_moves[depth][1] = killer_moves[depth][0]
                        killer_moves[depth][0] = move
                    history_table[move.from_square][move.to_square] += depth * depth
                break
        best_score = max_eval
        
    else:
        min_eval = math.inf
        for move in order_moves(board, list(board.legal_moves), depth, tt_move):
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True, start_time, time_limit)
            board.pop()
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
                
            beta = min(beta, eval_score)
            if beta <= alpha:
                if not board.is_capture(move):
                    if killer_moves[depth][0] != move:
                        killer_moves[depth][1] = killer_moves[depth][0]
                        killer_moves[depth][0] = move
                    history_table[move.from_square][move.to_square] += depth * depth
                break
        best_score = min_eval

    # --- 2. TT WRITE ---
    if best_score <= alpha_orig:
        flag = UPPERBOUND
    elif best_score >= beta:
        flag = LOWERBOUND
    else:
        flag = EXACT
        
    TRANSPOSITION_TABLE[board_hash] = {
        'score': best_score,
        'depth': depth,
        'flag': flag,
        'best_move': best_move
    }

    return best_score

# ---------------- MAIN MOVE ---------------- #

def next_move(fen):
    board = chess.Board(fen)

    for move in board.legal_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return str(move)
        board.pop()
    
    random.seed(int(time.time() * 1000) + hash(fen))
    current_position = board.board_fen()
    # if current_position in OPENING_BOOK:
    #     # Verify the book move is actually legal just to be safe
    #     book_move = chess.Move.from_uci(OPENING_BOOK[current_position])
    #     if book_move in board.legal_moves:
    #         return str(book_move)

    if current_position in OPENING_BOOK:
        # 1. Pull the list of possible moves for this position
        possible_book_moves = OPENING_BOOK[current_position]
        
        # 2. Randomly select one to ensure variety across different games
        chosen_book_move_str = random.choice(possible_book_moves)
        book_move = chess.Move.from_uci(chosen_book_move_str)
        
        # 3. Verify legality before executing
        if book_move in board.legal_moves:
            return str(book_move)

    start_time = time.time()
    time_limit = 3.5

    best_move_overall = None
    is_white = board.turn == chess.WHITE
    # best_score = -math.inf if board.turn == chess.WHITE else math.inf

    best_move_overall=list(board.legal_moves)[0]

    for depth in range(1, 11):
        try:
            best_score = -math.inf if board.turn == chess.WHITE else math.inf
            current_depth_best_move = None

            alpha = -math.inf
            beta = math.inf
            
            for move in order_moves(board, list(board.legal_moves), depth):
                board.push(move)

                # minimax depth 2
                score = minimax(board, depth - 1, alpha, beta, not is_white, start_time, time_limit)

                if is_white and score > 90000:
                    board.pop()
                    return str(move)
                elif not is_white and score < -90000:
                    board.pop()
                    return str(move)

                board.pop()

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
            if current_depth_best_move:
                best_move_overall = current_depth_best_move

        except SearchTimeout:
            # The clock ran out mid-search. Discard the incomplete depth and break the loop.
            break
    return str(best_move_overall)
