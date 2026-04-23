# bot_random.py

import chess
import random

def next_move(fen):
    board = chess.Board(fen)
    moves = list(board.legal_moves)
    
    if not moves:
        return None
    
    return str(random.choice(moves))