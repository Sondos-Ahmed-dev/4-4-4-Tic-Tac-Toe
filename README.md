# 4x4x4 Tic Tac Toe (3D)

A Python implementation of a **3D Tic Tac Toe game (4x4x4 grid)** with an AI agent using the Minimax algorithm with Alpha-Beta pruning.

---

## Features

* 3D Tic Tac Toe board (4x4x4)
* AI Agent using:

  * Minimax Algorithm
  * Alpha-Beta Pruning
* Two heuristic evaluation strategies:

  * H1: Based on available moves
  * H2: Based on center control
* Smart move selection with randomness for equal scores

---

## Project Structure

```
.
├── main.py          # Game loop
├── board.py         # Board logic
├── ai_agent.py      # AI (Minimax + Heuristics)
└── README.md
```

---

## How It Works

The AI uses the **Minimax algorithm** to simulate all possible moves up to a certain depth:

* Maximizing player → AI (-1)
* Minimizing player → Human (1)

### Alpha-Beta Pruning

Improves performance by cutting unnecessary branches.

---

## Heuristics

### H1:

* Counts available moves
* More moves = better position

### H2:

* Rewards controlling center positions
* Penalizes opponent control

---

##  How to Run

1. Make sure you have Python installed
2. Run the game:

```bash
python main.py
```

---

##  Example AI Code Snippet

```python
def find_best_move(board):
    CURRENT_HEURISTIC = evaluate_H2
    moves = board.get_available_moves()
    
    best_score = -999999
    best_moves = []

    for z, y, x in moves:
        board.board[z][y][x] = -1
        score = minimax(board, MAX_DEPTH - 1, False, -999999, 999999, CURRENT_HEURISTIC)
        board.board[z][y][x] = 0

        if score > best_score:
            best_score = score
            best_moves = [(z, y, x)]
        elif score == best_score:
            best_moves.append((z, y, x))

    return random.choice(best_moves)
```

---

## Future Improvements

* GUI using Tkinter or Pygame
* Adjustable difficulty
* Online multiplayer

---

##  Author

Sondos Ahmed Ibrahim
