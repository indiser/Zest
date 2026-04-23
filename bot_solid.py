import chess

# Basic material values
piece_value = { chess.PAWN: 100, chess.KNIGHT: 300, chess.BISHOP: 300, chess.ROOK: 500, chess.QUEEN: 900, chess.KING: 0 }

# Encourage center control
center_pst = [
    0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,
    0,  0, 10, 10, 10, 10,  0,  0,
    0,  0, 10, 20, 20, 10,  0,  0,
    0,  0, 10, 20, 20, 10,  0,  0,
    0,  0, 10, 10, 10, 10,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0,
    0,  0,  0,  0,  0,  0,  0,  0
]

def evaluate_shallow(board):
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            val = piece_value[piece.piece_type]
            # Add center control bonus for all pieces
            pst_index = square if piece.color == chess.WHITE else chess.square_mirror(square)
            val += center_pst[pst_index]
            score += val if piece.color == chess.WHITE else -val
    return score

def next_move(fen):
    board = chess.Board(fen)
    best_move = None
    is_white = board.turn == chess.WHITE
    best_score = -float('inf') if is_white else float('inf')

    # Depth 1 Search: Only looks at the immediate result of its move
    for move in board.legal_moves:
        board.push(move)
        score = evaluate_shallow(board)
        board.pop()

        if is_white and score > best_score:
            best_score = score
            best_move = move
        elif not is_white and score < best_score:
            best_score = score
            best_move = move

    if best_move:
        return str(best_move)
    return str(list(board.legal_moves)[0])