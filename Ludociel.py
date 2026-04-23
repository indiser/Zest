import chess
import math
import time

piece_value = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

EVAL_CACHE = {}

# ---------------- OPENING BOOK ---------------- #
# Maps a board state (FEN without counters) to a specific UCI move.
# This forces the bot to play standard center-control openings.

# ---------------- OPENING BOOK ---------------- #
OPENING_BOOK = {
    # --- WHITE: e4 Openings ---
    "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR": "e2e4", # Move 1
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR": "g1f3", # e4 e5 -> Nf3
    "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R": "f1c4", # Italian Game
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R": "e1g1", # Castle in Italian
    
    # --- WHITE: Against the Sicilian (c5) ---
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR": "g1f3", # e4 c5 -> Nf3
    "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R": "d2d4", # Open Sicilian
    "rnbqkbnr/pp2pppp/3p4/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R": "d2d4", # Open Sicilian

    # --- WHITE: Against the French (e6) ---
    "rnbqkbnr/pppp1ppp/4p3/8/4P3/8/PPPP1PPP/RNBQKBNR": "d2d4", # e4 e6 -> d4
    "rnbqkbnr/pppp1ppp/4p3/8/3PP3/8/PPP2PPP/RNBQKBNR": "b1c3", # e4 e6 d4 d5 -> Nc3

    # --- BLACK: Defending against e4 ---
    "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR": "e7e5", # Respond to e4 with e5
    "rnbqkbnr/pppp1ppp/8/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R": "b8c6", # Defend pawn with Nc6
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R": "g8f6", # Two Knights Defense
    "r1bqkbnr/pppp1ppp/2n5/1B2p3/4P3/5N2/PPPP1PPP/RNBQK2R": "a7a6", # Ruy Lopez -> a6

    # --- BLACK: Defending against d4 ---
    "rnbqkbnr/pppppppp/8/8/3P4/8/PPP1PPPP/RNBQKBNR": "d7d5", # Respond to d4 with d5
    "rnbqkbnr/ppp1pppp/8/3p4/2PP4/8/PP2PPPP/RNBQKBNR": "e7e6", # Queen's Gambit Declined
    "rnbqkbnr/ppp1pppp/8/3p4/3P4/5N2/PPP1PPPP/RNBQKB1R": "g8f6", # Develop Knight
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
     0,  0,  0,  0,  0,  0,  0,  0,
     5, 10, 10, 10, 10, 10, 10,  5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
    -5,  0,  0,  0,  0,  0,  0, -5,
     0,  0,  0,  5,  5,  0,  0,  0
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
    
    board_hash = board.fen().rsplit(' ', 2)[0]
    if board_hash in EVAL_CACHE:
        return EVAL_CACHE[board_hash]

    # draw situations
    if (board.is_stalemate() or 
        board.is_insufficient_material() or 
        board.can_claim_fifty_moves()):
        return 0

    # discourage repetition
    if board.can_claim_threefold_repetition():
        return 0
    
    if (board.is_stalemate() or 
        board.is_insufficient_material() or 
        board.can_claim_fifty_moves() or
        board.can_claim_threefold_repetition()):
        return 0

    score = 0

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
                value += pawn_pst[pst_index]
            elif piece.piece_type == chess.BISHOP:
                pst_index = square if piece.color == chess.WHITE else chess.square_mirror(square)
                value += bishop_pst[pst_index]
            elif piece.piece_type == chess.ROOK:
                pst_index = square if piece.color == chess.WHITE else chess.square_mirror(square)
                value += rook_pst[pst_index]
            elif piece.piece_type == chess.QUEEN:
                pst_index = square if piece.color == chess.WHITE else chess.square_mirror(square)
                value += queen_pst[pst_index]
            elif piece.piece_type == chess.KING:
                pst_index = square if piece.color == chess.WHITE else chess.square_mirror(square)
                value += king_pst[pst_index]
            score += value if piece.color == chess.WHITE else -value
    
    if abs(score) > 400: 
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


    # check pressure (fixed logic)

    if board.is_check():
        if board.turn == chess.WHITE:
            score -= 2
        else:
            score += 2
    
    mobility = board.legal_moves.count()
    if board.turn == chess.WHITE:
        score += mobility * 0.1  
    else:
        score -= mobility * 0.1

    EVAL_CACHE[board.fen().rsplit(' ', 2)[0]] = score
    return score

# ---------------- MOVE ORDERING ---------------- #

def order_moves(board, moves):
    def guess_move_score(move):
        score = 0
        
        # 1. Prioritize Captures using MVV-LVA
        if board.is_capture(move):
            attacker = board.piece_at(move.from_square)
            victim = board.piece_at(move.to_square)
            
            # If there's a direct victim, score it. (Multiplying victim by 10 makes it the priority)
            if victim and attacker:
                score += 10 * piece_value[victim.piece_type] - piece_value[attacker.piece_type]
            else:
                # Fallback for En Passant (where the to_square is technically empty)
                score += 10
                
        # 2. Prioritize Promotions based on the piece being promoted to
        if move.promotion:
            score += piece_value[move.promotion] * 10
            
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
    captures = [move for move in board.legal_moves if board.is_capture(move)]
    
    if maximizing:
        max_eval = eval_score
        for move in order_moves(board, captures):
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
        for move in order_moves(board, captures):
            board.push(move)
            score = quiescence(board, alpha, beta, True, start_time, time_limit)
            board.pop()
            min_eval = min(min_eval, score)
            beta = min(beta, score)
            if beta <= alpha:
                break
        return min_eval
    

# ---------------- MINIMAX ---------------- #

def minimax(board, depth, alpha, beta, maximizing,  start_time, time_limit):
    if time.time() - start_time > time_limit:
        raise SearchTimeout()

    if board.can_claim_threefold_repetition():
        return 0
    
    if depth == 0:
        return quiescence(board, alpha, beta, maximizing, start_time, time_limit)
    if board.is_game_over():
        return evaluate(board, depth)
    

    if maximizing:
        max_eval = -math.inf

        for move in order_moves(board, list(board.legal_moves)):
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, False, start_time, time_limit)
            board.pop()
            max_eval = max(max_eval, eval_score)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval

    else:
        min_eval = math.inf

        for move in order_moves(board, list(board.legal_moves)):
            board.push(move)
            eval_score = minimax(board, depth - 1, alpha, beta, True, start_time, time_limit)
            board.pop()
            min_eval = min(min_eval, eval_score)
            beta=min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval


# ---------------- MAIN MOVE ---------------- #

def next_move(fen):
    board = chess.Board(fen)

    for move in board.legal_moves:
        board.push(move)
        if board.is_checkmate():
            board.pop()
            return str(move)
        board.pop()

    current_position = board.board_fen()
    if current_position in OPENING_BOOK:
        # Verify the book move is actually legal just to be safe
        book_move = chess.Move.from_uci(OPENING_BOOK[current_position])
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
            
            for move in order_moves(board, list(board.legal_moves)):
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
