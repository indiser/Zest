import chess

# piece values
piece_value = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}

def next_move(fen):
    board = chess.Board(fen)

    best_move = None
    best_value = -1

    for move in board.legal_moves:
        if board.is_capture(move):
            piece = board.piece_at(move.to_square)

            if piece:
                value = piece_value[piece.piece_type]

                if value > best_value:
                    best_value = value
                    best_move = move

    if best_move:
        return str(best_move)

    # fallback → random
    return str(list(board.legal_moves)[0])