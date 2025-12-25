# Chess Opening Trainer

A customizable chess opening trainer with a visual chess board that helps you memorize opening lines with weighted random variations.

## Features

- **Visual chess board** with Unicode pieces
- Define custom opening lines with multiple variations
- Weighted probabilities for computer moves (e.g., 60% e6, 40% e5)
- Validates your moves against the correct repertoire
- Follows preset lines until they end or you make an incorrect move
- Save/load opening repertoires from JSON files
- Play as White or Black
- Real-time board updates after each move

## Installation

Requirements:
- Python 3.7+
- No external dependencies needed

Download `chess_opening_trainer.py` and run it. 

## Quick Start

```bash
python chess_opening_trainer.py
```

Choose option 1 to try the example opening, which demonstrates: 
- Visual board display
- French Defense and Ruy Lopez variations
- Weighted move probabilities

## Visual Board Display

The board uses Unicode chess symbols and updates after every move: 

```
   a b c d e f g h
  ┌─────────────────┐
8 │ ♜ ♞ ♝ ♛ ♚ ♝ ♞ ♜ │ 8
7 │ ♟ ♟ ♟ ♟ ♟ ♟ ♟ ♟ │ 7
6 │ · · · · · · · · │ 6
5 │ · · · · · · · · │ 5
4 │ · · · · ♙ · · · │ 4
3 │ · · · · · · · · │ 3
2 │ ♙ ♙ ♙ ♙ · ♙ ♙ ♙ │ 2
1 │ ♖ ♘ ♗ ♕ ♔ ♗ ♘ ♖ │ 1
  └─────────────────┘
   a b c d e f g h
```

Legend:
- **White pieces**: ♔ ♕ ♖ ♗ ♘ ♙ (King, Queen, Rook, Bishop, Knight, Pawn)
- **Black pieces**: ♚ ♛ ♜ ♝ ♞ ♟
- **Empty squares**: ·

## Creating Your Own Openings

### JSON Format

Create a JSON file with your opening repertoire:

```json
{
  "start": "white",
  "tree": {
    "": {
      "player": false,
      "moves":  [["e4", 1.0]]
    },
    "e4": {
      "player": true,
      "moves":  [["e5", 0.6], ["c5", 0.4]]
    },
    "e4-e5": {
      "player": false,
      "moves": [["Nf3", 1.0]]
    },
    "e4-c5": {
      "player":  false,
      "moves": [["Nf3", 0.7], ["Nc3", 0.3]]
    }
  }
}
```

### Format Explanation

- **`start`**: `"white"` if you're playing White, `"black"` if you're playing Black
- **`tree`**: Dictionary of positions
  - **Key**: Position notation (moves separated by `-`, empty string for starting position)
  - **`player`**: 
    - `true` = Your turn (computer checks if your move is correct)
    - `false` = Computer's turn (makes random weighted move)
  - **`moves`**: List of `[move, weight]` pairs
    - For computer moves: weights determine probability
    - For your moves: all listed moves are considered correct

### Example:  King's Indian Defense as Black

```json
{
  "start": "black",
  "tree": {
    "": {
      "player": false,
      "moves": [["d4", 0.8], ["e4", 0.15], ["Nf3", 0.05]]
    },
    "d4": {
      "player": true,
      "moves": [["Nf6", 1.0]]
    },
    "d4-Nf6": {
      "player": false,
      "moves": [["c4", 0.7], ["Nf3", 0.2], ["Bg5", 0.1]]
    },
    "d4-Nf6-c4": {
      "player": true,
      "moves": [["g6", 1.0]]
    },
    "d4-Nf6-c4-g6": {
      "player": false,
      "moves": [["Nc3", 0.6], ["Nf3", 0.4]]
    },
    "d4-Nf6-c4-g6-Nc3": {
      "player": true,
      "moves": [["Bg7", 1.0]]
    },
    "d4-Nf6-c4-g6-Nc3-Bg7": {
      "player": false,
      "moves": [["e4", 0.7], ["Nf3", 0.3]]
    }
  }
}
```

## How It Works

1. **Computer's Turn**:  Randomly selects from available moves using weighted probabilities
2. **Your Turn**: You input a move, and the program checks if it matches any correct option
3. **Board Updates**: After each move, the board is automatically updated and displayed
4. **Continues**:  Follows the tree until you make an incorrect move or reach the end of the line

## Commands During Play

- Type your move in algebraic notation (e.g., `e4`, `Nf3`, `O-O`)
- `quit` - Exit the program
- `reset` - Start over from the beginning
- `line` - Show the current move sequence
- `board` - Redisplay the current board position

## Move Notation

Use standard algebraic notation:
- **Pawn moves**: `e4`, `d5`, `e5`
- **Piece moves**: `Nf3` (Knight), `Bc4` (Bishop), `Qd4` (Queen), `Rad1` (Rook)
- **Castling**: `O-O` (kingside), `O-O-O` (queenside)
- **Captures**: `exd5`, `Nxe5`, `Bxc6`

## Tips

- Start with a small repertoire and expand gradually
- Use weights to practice against more common responses more frequently
- Create separate files for different openings
- Review the `example_opening.json` and `french_defense.json` files for reference
- The visual board helps you verify positions and catch notation errors

## Example Opening Files Included

1. **example_opening.json** - Mixed repertoire with French Defense and Ruy Lopez
2. **french_defense.json** - Complete French Defense repertoire for Black

## File Structure

```
chess_opening_trainer.py    # Main program
example_opening.json        # Auto-generated example
french_defense. json        # French Defense repertoire
```

## Features of the Visual Board

- Displays after every move
- Shows rank and file labels (1-8, a-h)
- Uses clear Unicode chess symbols
- Updates in real-time as you practice
- Helps verify you're following the correct line
- Can be redisplayed anytime with the `board` command

## Future Enhancements

Potential additions:
- Highlighted last move
- Move history sidebar
- PGN import/export
- Statistics tracking
- Spaced repetition algorithm
- Multiple board themes
- Save progress between sessions
