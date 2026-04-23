# Zest - Chess Engine Prototype

A Python-based chess engine prototype featuring multiple AI bots with varying skill levels, from simple heuristic-based players to advanced minimax engines with sophisticated evaluation functions.

## Overview

Zest is a modular chess bot framework designed to explore different chess AI strategies. The project includes several bot implementations ranging from random move selection to deep search algorithms with transposition tables, killer move heuristics, and advanced position evaluation.

**Current Status:** Python prototype with future plans to rewrite in C/C++ with neural networks and Stockfish-level strength targeting 10,000+ Elo.

## Features

### Core Engine (Zest)
- **Minimax with Alpha-Beta Pruning** - Efficient game tree search
- **Transposition Table** - Zobrist hashing for position caching (1M entries)
- **Quiescence Search** - Tactical move evaluation to avoid horizon effect
- **Move Ordering** - MVV-LVA, killer moves, history heuristic, and TT move prioritization
- **Late Move Reduction (LMR)** - Reduces search depth for quiet moves
- **Null Move Pruning** - Prunes branches with null moves
- **Aspiration Windows** - Narrows alpha-beta bounds for faster convergence
- **Opening Book** - Predefined opening moves for standard positions
- **Advanced Evaluation:**
  - Material + Piece-Square Tables (PST)
  - King safety scoring
  - Mobility evaluation
  - Mop-up bonus for endgames
  - Tempo/conversion penalties

### Bot Variants

| Bot | Strategy | Depth | Strength |
|-----|----------|-------|----------|
| **Zest** | Full minimax + advanced eval | 11 | Strong |
| **MorningStar** | Minimax + pawn structure analysis | 11 | Strong |
| **Trinity** | Minimax + king safety focus | 10 | Strong |
| **Chaos God** | Aggressive minimax + inflated piece values | 10 | Strong |
| **Ludociel** | Lightweight minimax + simple eval | 10 | Intermediate |
| **Rafael** | Minimax + killer moves & history heuristic | 10 | Strong |
| **bot_solid** | Depth-1 search + center control | 1 | Intermediate |
| **bot_greedy** | Greedy capture selection | 0 | Weak |
| **bot_random** | Random legal moves | 0 | Weak |

### Advanced Features (MorningStar)
- Passed pawn detection and bonuses
- Doubled/isolated pawn penalties
- Rook open file evaluation
- Bishop pair bonus
- Sophisticated king safety with attacker proximity

## Project Structure

```
Zest/
├── zest.py              # Main engine with minimax + advanced eval
├── MorningStar.py       # Enhanced engine with pawn structure analysis
├── Trinity.py           # Alternative minimax implementation
├── Chaos God.py         # Aggressive minimax with inflated piece values
├── Ludociel.py          # Lightweight minimax engine
├── Rafael.py            # Minimax with killer moves & history heuristic
├── bot_solid.py         # Depth-1 evaluation bot
├── bot_greedy.py        # Greedy capture bot
├── bot_random.py        # Random move bot
├── app.py               # Flask web server for bot battles
├── gauglet_elo.py       # ELO rating calculator for bot tournaments
├── templates/
│   ├── index.html       # Single player interface
│   └── colosium.html    # Bot arena/tournament interface
├── requirements.txt     # Python dependencies
└── Readme.md           # This file
```

## Installation

### Requirements
- Python 3.8+
- `chess` library (python-chess)
- `Flask` (for web interface)

### Setup

```bash
# Create virtual environment
python -m venv env
source env/Scripts/activate  # Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Web Interface

```bash
python app.py
```

Then navigate to:
- **Single Player:** `http://localhost:5000/`
- **Bot Arena:** `http://localhost:5000/bots`

### Direct API

```python
import zest

fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"
move = zest.next_move(fen)
print(move)  # e2e4
```

## Engine Parameters

### Search Configuration
- **Time Limit:** 3.5 seconds per move
- **Max Transposition Table Size:** 1,000,000 entries
- **Aspiration Window:** ±50 centipawns
- **Null Move Reduction:** R=2 (depth < 6) or R=3 (depth ≥ 6)

### Evaluation Weights
- **Piece Values:** Pawn=1, Knight/Bishop=3, Rook=5, Queen=9
- **Mobility Weight:** 0.1 (midgame), 3.0 (endgame)
- **Mop-up Bonus:** 20 per king distance unit
- **King Safety:** ±15-50 per pawn shield/open file

## Future Improvements

### Planned Enhancements
1. **C/C++ Rewrite** - 100x+ performance improvement
2. **Neural Network Evaluation** - Deep learning-based position assessment
3. **Stockfish Integration** - Hybrid approach combining classical + neural methods
4. **NNUE (Efficiently Updatable Neural Networks)** - Fast incremental evaluation
5. **Endgame Tablebases** - Perfect play in simplified positions
6. **Parallel Search** - Multi-threaded alpha-beta pruning
7. **Opening/Endgame Books** - Expanded databases

### Target
**10,000+ Elo** - Superhuman strength capable of crushing all existing bots

## Performance Notes

- **Current Strength:** ~2000-2500 Elo (estimated)
- **Search Depth:** Typically 8-11 plies in 3.5 seconds
- **Bottleneck:** Python interpretation; C++ rewrite will enable deeper searches

## Architecture Decisions

### Why Minimax + Alpha-Beta?
- Proven, deterministic approach
- Foundation for neural network integration
- Easier to debug and understand than pure neural methods

### Why Transposition Tables?
- Eliminates redundant position evaluations
- Critical for reaching deeper search depths
- Zobrist hashing provides O(1) lookups

### Why Quiescence Search?
- Prevents horizon effect (missing tactical blows)
- Stabilizes evaluation at leaf nodes
- Limits search to captures/promotions/checks

## Testing & Benchmarking

Run bot matchups via the web arena:
```
http://localhost:5000/bots
```

Select two bots and watch them compete. Results are logged in the console.

## Contributing

This is a personal project exploring chess AI. Contributions welcome for:
- Bug fixes
- Performance optimizations
- New evaluation features
- Test cases

## License

Open source - feel free to use and modify.

## References

- [python-chess](https://python-chess.readthedocs.io/) - Chess library
- [Stockfish](https://stockfishchess.org/) - Inspiration for evaluation
- [Chess Programming Wiki](https://www.chessprogramming.org/) - Algorithm references

---

**Author:** Indiser.  
**Status:** Active Development (Python Prototype)  
**Next Phase:** C/C++ Rewrite with Neural Networks
