import random
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

class Player(Enum):
    WHITE = "white"
    BLACK = "black"

@dataclass
class Move:
    """Represents a single move option"""
    notation: str
    weight: float = 1.0  # Probability weight for computer moves


class ChessBoard:
    """Represents and displays a chess board"""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset board to starting position"""
        self.board = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],  # Black back rank
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],  # Black pawns
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['.', '.', '.', '.', '.', '.', '.', '.'],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],  # White pawns
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R'],  # White back rank
        ]
        self.white_king_moved = False
        self.black_king_moved = False
        self.white_rook_a_moved = False
        self.white_rook_h_moved = False
        self.black_rook_a_moved = False
        self.black_rook_h_moved = False

    def square_to_coords(self, square: str) -> Tuple[int, int]:
        """Convert algebraic notation to board coordinates"""
        file = ord(square[0].lower()) - ord('a')  # a-h -> 0-7
        rank = 8 - int(square[-1])  # 1-8 -> 7-0
        return rank, file

    def coords_to_square(self, rank: int, file: int) -> str:
        """Convert board coordinates to algebraic notation"""
        return chr(file + ord('a')) + str(8 - rank)

    def parse_move(self, move: str, is_white_turn: bool) -> Optional[Tuple[Tuple[int, int], Tuple[int, int], str]]:
        """
        Parse algebraic notation and return (from_pos, to_pos, piece_type)
        Returns None if move cannot be parsed
        """
        original_move = move
        move = move.strip().replace('+', '').replace('#', '').replace('!', '').replace('?', '')

        # Castling
        if move in ['O-O', '0-0', 'o-o', 'O-o', 'o-O']:
            rank = 7 if is_white_turn else 0
            return ((rank, 4), (rank, 6), 'K' if is_white_turn else 'k')
        if move in ['O-O-O', '0-0-0', 'o-o-o']:
            rank = 7 if is_white_turn else 0
            return ((rank, 4), (rank, 2), 'K' if is_white_turn else 'k')

        # Determine piece type
        if move[0].isupper():
            piece_char = move[0]
            move_part = move[1:]
        else:
            piece_char = 'P'  # Pawn
            move_part = move

        piece = piece_char.upper() if is_white_turn else piece_char.lower()

        # Handle captures and disambiguation
        is_capture = 'x' in move_part
        move_part = move_part.replace('x', '')

        # Destination square (last 2 characters)
        if len(move_part) < 2:
            return None
        dest_square = move_part[-2:]
        try:
            to_rank, to_file = self.square_to_coords(dest_square)
        except Exception:
            return None

        # Disambiguation (e.g., Nbd2, R1e1, exd5)
        from_file_hint = None
        from_rank_hint = None
        disambig = move_part[:-2]
        if disambig:
            # File hint (letter)
            for ch in disambig:
                if ch.isalpha() and 'a' <= ch.lower() <= 'h':
                    from_file_hint = ord(ch.lower()) - ord('a')
            # Rank hint (digit)
            for ch in disambig:
                if ch.isdigit():
                    from_rank_hint = 8 - int(ch)

        # Find the piece that can move to destination
        from_pos = self.find_piece(piece, to_rank, to_file, from_file_hint, from_rank_hint, is_white_turn, is_capture)
        if from_pos:
            return (from_pos, (to_rank, to_file), piece)
        return None

    def find_piece(
        self,
        piece: str,
        to_rank: int,
        to_file: int,
        from_file_hint: Optional[int],
        from_rank_hint: Optional[int],
        is_white_turn: bool,
        is_capture: bool
    ) -> Optional[Tuple[int, int]]:
        """Find which piece can move to the destination"""
        piece_type = piece.upper()

        # Pawn moves
        if piece_type == 'P':
            if is_white_turn:
                # Captures
                if is_capture:
                    candidate_files = []
                    if from_file_hint is not None:
                        candidate_files = [from_file_hint]
                    else:
                        candidate_files = [to_file - 1, to_file + 1]
                    for f in candidate_files:
                        r = to_rank + 1
                        if 0 <= r < 8 and 0 <= f < 8:
                            if self.board[r][f] == 'P':
                                return (r, f)
                # Single push
                if to_rank + 1 < 8 and self.board[to_rank + 1][to_file] == 'P' and self.board[to_rank][to_file] == '.':
                    return (to_rank + 1, to_file)
                # Double push from starting rank (e2->e4)
                if (
                    to_rank == 4 and
                    self.board[6][to_file] == 'P' and
                    self.board[5][to_file] == '.' and
                    self.board[4][to_file] == '.'
                ):
                    return (6, to_file)
            else:
                # Black pawn
                # Captures
                if is_capture:
                    candidate_files = []
                    if from_file_hint is not None:
                        candidate_files = [from_file_hint]
                    else:
                        candidate_files = [to_file - 1, to_file + 1]
                    for f in candidate_files:
                        r = to_rank - 1
                        if 0 <= r < 8 and 0 <= f < 8:
                            if self.board[r][f] == 'p':
                                return (r, f)
                # Single push
                if to_rank - 1 >= 0 and self.board[to_rank - 1][to_file] == 'p' and self.board[to_rank][to_file] == '.':
                    return (to_rank - 1, to_file)
                # Double push from starting rank (e7->e5)
                if (
                    to_rank == 3 and
                    self.board[1][to_file] == 'p' and
                    self.board[2][to_file] == '.' and
                    self.board[3][to_file] == '.'
                ):
                    return (1, to_file)

        # Knight moves
        elif piece_type == 'N':
            knight_moves = [(-2, -1), (-2, 1), (-1, -2), (-1, 2),
                            (1, -2), (1, 2), (2, -1), (2, 1)]
            for dr, df in knight_moves:
                r, f = to_rank + dr, to_file + df
                if 0 <= r < 8 and 0 <= f < 8:
                    if self.board[r][f] == piece:
                        if (from_rank_hint is None or r == from_rank_hint) and \
                           (from_file_hint is None or f == from_file_hint):
                            return (r, f)

        # Bishop moves
        elif piece_type == 'B':
            for dr, df in [(-1, -1), (-1, 1), (1, -1), (1, 1)]:
                r, f = to_rank + dr, to_file + df
                while 0 <= r < 8 and 0 <= f < 8:
                    if self.board[r][f] == piece:
                        if (from_rank_hint is None or r == from_rank_hint) and \
                           (from_file_hint is None or f == from_file_hint):
                            return (r, f)
                    if self.board[r][f] != '.':
                        break
                    r, f = r + dr, f + df

        # Rook moves
        elif piece_type == 'R':
            for dr, df in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                r, f = to_rank + dr, to_file + df
                while 0 <= r < 8 and 0 <= f < 8:
                    if self.board[r][f] == piece:
                        if (from_rank_hint is None or r == from_rank_hint) and \
                           (from_file_hint is None or f == from_file_hint):
                            return (r, f)
                    if self.board[r][f] != '.':
                        break
                    r, f = r + dr, f + df

        # Queen moves (combination of rook and bishop)
        elif piece_type == 'Q':
            for dr, df in [(-1, -1), (-1, 0), (-1, 1), (0, -1),
                           (0, 1), (1, -1), (1, 0), (1, 1)]:
                r, f = to_rank + dr, to_file + df
                while 0 <= r < 8 and 0 <= f < 8:
                    if self.board[r][f] == piece:
                        if (from_rank_hint is None or r == from_rank_hint) and \
                           (from_file_hint is None or f == from_file_hint):
                            return (r, f)
                    if self.board[r][f] != '.':
                        break
                    r, f = r + dr, f + df

        # King moves
        elif piece_type == 'K':
            for dr in [-1, 0, 1]:
                for df in [-1, 0, 1]:
                    if dr == 0 and df == 0:
                        continue
                    r, f = to_rank + dr, to_file + df
                    if 0 <= r < 8 and 0 <= f < 8:
                        if self.board[r][f] == piece:
                            return (r, f)

        return None

    def make_move(self, move: str, is_white_turn: bool) -> bool:
        """Make a move on the board. Returns True if successful."""
        move = move.replace('+', '').replace('#', '')
        parsed = self.parse_move(move, is_white_turn)
        if not parsed:
            return False

        from_pos, to_pos, piece = parsed
        from_rank, from_file = from_pos
        to_rank, to_file = to_pos

        # Handle castling
        if move in ['O-O', '0-0', 'o-o', 'O-o', 'o-O']:
            rank = 7 if is_white_turn else 0
            self.board[rank][4] = '.'
            self.board[rank][6] = 'K' if is_white_turn else 'k'
            self.board[rank][7] = '.'
            self.board[rank][5] = 'R' if is_white_turn else 'r'
            if is_white_turn:
                self.white_king_moved = True
            else:
                self.black_king_moved = True
            return True
        if move in ['O-O-O', '0-0-0', 'o-o-o']:
            rank = 7 if is_white_turn else 0
            self.board[rank][4] = '.'
            self.board[rank][2] = 'K' if is_white_turn else 'k'
            self.board[rank][0] = '.'
            self.board[rank][3] = 'R' if is_white_turn else 'r'
            if is_white_turn:
                self.white_king_moved = True
            else:
                self.black_king_moved = True
            return True

        # Normal move
        moving_piece = self.board[from_rank][from_file]
        self.board[from_rank][from_file] = '.'
        self.board[to_rank][to_file] = moving_piece

        # Track king and rook moves for castling rights
        if moving_piece == 'K':
            self.white_king_moved = True
        elif moving_piece == 'k':
            self.black_king_moved = True
        elif moving_piece == 'R':
            if from_rank == 7 and from_file == 0:
                self.white_rook_a_moved = True
            elif from_rank == 7 and from_file == 7:
                self.white_rook_h_moved = True
        elif moving_piece == 'r':
            if from_rank == 0 and from_file == 0:
                self.black_rook_a_moved = True
            elif from_rank == 0 and from_file == 7:
                self.black_rook_h_moved = True

        return True

    def display(self):
        """Display the chess board with Unicode pieces"""
        piece_symbols = {
            'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
            'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟',
            '.': '·'
        }

        print("\n   a b c d e f g h")
        print("  ┌─────────────────┐")
        for rank in range(8):
            print(f"{8 - rank} │", end=" ")
            for file in range(8):
                piece = self.board[rank][file]
                symbol = piece_symbols.get(piece, piece)
                print(symbol, end=" ")
            print(f"│ {8 - rank}")
        print("  └─────────────────┘")
        print("   a b c d e f g h\n")


class OpeningTrainer:
    def __init__(self):
        self.opening_tree: Dict = {}
        self.current_position: List[str] = []
        self.player_color: Player = Player.WHITE
        self.board = ChessBoard()

    def build_simple_tree(self, lines: Dict[str, any]):
        """
        Build opening tree from a simpler format.

        Format:
        {
            'start': 'white',  # which color the player plays
            'tree': {
                '':  {  # Initial position
                    'player': False,  # Computer's turn
                    'moves': [['e4', 1.0]]
                },
                'e4': {
                    'player': True,  # Player's turn
                    'moves': [['e6', 0.6], ['e5', 0.4]]  # Correct moves
                },
                # ... etc
            }
        }
        """
        self.player_color = Player.WHITE if lines.get('start', 'white') == 'white' else Player.BLACK
        self.opening_tree = lines.get('tree', {})

    def get_position_key(self) -> str:
        """Get the current position key"""
        return '-'.join(self.current_position)

    def is_player_turn(self) -> bool:
        """Determine if it's the player's turn based on the opening tree state"""
        pos_key = self.get_position_key()
        node = self.opening_tree.get(pos_key)
        if node is not None:
            return bool(node.get('player', False))
        return False

    def get_current_options(self) -> Optional[List]:
        """Get available moves for current position"""
        pos_key = self.get_position_key()
        if pos_key in self.opening_tree:
            return self.opening_tree[pos_key].get('moves', [])
        return None

    def make_computer_move(self) -> Optional[str]:
        """Computer makes a weighted random move"""
        options = self.get_current_options()
        if not options:
            return None

        # Extract moves and weights - handles list/tuple/dict
        moves = []
        weights = []
        for opt in options:
            if isinstance(opt, (list, tuple)) and len(opt) >= 1:
                moves.append(opt[0])
                weights.append(opt[1] if len(opt) > 1 else 1.0)
            elif isinstance(opt, dict) and 'move' in opt:
                moves.append(opt['move'])
                weights.append(opt.get('weight', 1.0))
            else:
                moves.append(str(opt))
                weights.append(1.0)

        selected_move = random.choices(moves, weights=weights)[0]

        # Update board
        is_white_turn = len(self.current_position) % 2 == 0
        if not self.board.make_move(selected_move, is_white_turn):
            print(f"Warning: Could not apply move {selected_move} to board")

        self.current_position.append(selected_move)
        return selected_move

    def check_player_move(self, move: str) -> Tuple[bool, Optional[str]]:
        """
        Check if player's move is correct.

        Returns:
            (is_correct, message)
        """
        # Tiny improvement: handle accidental Enter presses
        move = move.strip()
        if not move:
            return False, "Empty move"

        options = self.get_current_options()
        if not options:
            return False, "No more moves in this line!"

        # Extract valid moves - handles list/tuple/dict
        valid_moves = []
        for opt in options:
            if isinstance(opt, (list, tuple)) and len(opt) >= 1:
                valid_moves.append(opt[0])
            elif isinstance(opt, dict) and 'move' in opt:
                valid_moves.append(opt['move'])
            else:
                valid_moves.append(str(opt))

        if move in valid_moves:
            # Update board
            is_white_turn = len(self.current_position) % 2 == 0
            if not self.board.make_move(move, is_white_turn):
                print(f"Warning: Could not apply move {move} to board")

            self.current_position.append(move)
            return True, "Correct!"
        else:
            return False, f"Incorrect! Valid moves: {', '.join(valid_moves)}"

    def reset(self):
        """Reset the position"""
        self.current_position = []
        self.board.reset()

    def get_current_line(self) -> str:
        """Get the current move sequence"""
        return ' '.join(self.current_position) if self.current_position else "Starting position"

    def has_more_moves(self) -> bool:
        """Check if there are more moves available"""
        pos_key = self.get_position_key()
        return pos_key in self.opening_tree and len(self.opening_tree[pos_key].get('moves', [])) > 0

    def display_board(self):
        """Display the current board position"""
        self.board.display()


def save_opening_to_file(opening_data: Dict, filename: str):
    """Save opening tree to JSON file"""
    with open(filename, 'w') as f:
        json.dump(opening_data, f, indent=2)

def load_opening_from_file(filename: str) -> Dict:
    """Load opening tree from JSON file"""
    with open(filename, 'r') as f:
        return json.load(f)


def create_example_opening() -> Dict:
    """Create the example opening you described"""
    return {
        'start': 'white',
        'tree': {
            '': {
                'player': False,
                'moves': [['e4', 1.0]]  # Computer plays e4
            },
            'e4': {
                'player': True,
                'moves': [['e6', 0.6], ['e5', 0.4]]  # Your move: e6 or e5
            },
            'e4-e6': {
                'player': False,
                'moves': [['d4', 1.0]]
            },
            'e4-e5': {
                'player': False,
                'moves': [['Nf3', 1.0]]
            },
            'e4-e6-d4': {
                'player': True,
                'moves': [['d5', 0.7], ['c5', 0.3]]
            },
            'e4-e5-Nf3': {
                'player': True,
                'moves': [['Nc6', 0.6], ['Nf6', 0.4]]
            },
            'e4-e6-d4-d5': {
                'player': False,
                'moves': [['Nc3', 0.5], ['Nd2', 0.5]]
            },
            'e4-e6-d4-c5': {
                'player': False,
                'moves': [['Nf3', 1.0]]
            },
            'e4-e5-Nf3-Nc6': {
                'player': False,
                'moves': [['Bb5', 0.7], ['Bc4', 0.3]]
            },
            'e4-e5-Nf3-Nf6': {
                'player': False,
                'moves': [['Nxe5', 1.0]]
            },
            'e4-e6-d4-d5-Nc3': {
                'player': True,
                'moves': [['Nf6', 0.8], ['Bb4', 0.2]]
            },
            'e4-e6-d4-d5-Nd2': {
                'player': True,
                'moves': [['Nf6', 0.9], ['c5', 0.1]]
            },
            'e4-e5-Nf3-Nc6-Bb5': {
                'player': True,
                'moves': [['a6', 0.6], ['Nf6', 0.3], ['f5', 0.1]]
            },
            'e4-e5-Nf3-Nc6-Bc4': {
                'player': True,
                'moves': [['Bc5', 0.5], ['Nf6', 0.5]]
            }
        }
    }


def main():
    """Main game loop"""
    print("=" * 60)
    print("CHESS OPENING TRAINER")
    print("=" * 60)
    print()

    # Initialize trainer
    trainer = OpeningTrainer()

    # Menu
    print("Choose an option:")
    print("1. Use example opening")
    print("2. Load opening from file")
    print("3. Create custom opening")

    choice = input("\nYour choice (1-3): ").strip()

    if choice == '1':
        opening_data = create_example_opening()
        trainer.build_simple_tree(opening_data)
        print("\nExample opening loaded!")
    elif choice == '2':
        filename = input("Enter filename: ").strip()
        try:
            opening_data = load_opening_from_file(filename)
            trainer.build_simple_tree(opening_data)
            print(f"\nOpening loaded from {filename}!")
        except FileNotFoundError:
            print("File not found! Using example opening instead.")
            opening_data = create_example_opening()
            trainer.build_simple_tree(opening_data)
    else:
        print("\nCustom opening builder coming soon! Using example for now.")
        opening_data = create_example_opening()
        trainer.build_simple_tree(opening_data)

    # Save example for reference
    save_opening_to_file(create_example_opening(), 'example_opening.json')
    print("(Example opening saved to 'example_opening.json' for reference)")

    print(f"\nYou are playing as: {trainer.player_color.value.upper()}")
    print("\nCommands: 'quit' to exit, 'reset' to start over, 'line' to see current line, 'board' to redisplay board")
    print("=" * 60)

    # Display initial board
    trainer.display_board()

    # Game loop
    while True:
        if not trainer.has_more_moves():
            print("\nCongratulations! You've reached the end of this opening line!")
            retry = input("\nStart over? (yes/no): ").strip().lower()
            if retry in ['yes', 'y']:
                trainer.reset()
                print("\nPosition reset!\n")
                trainer.display_board()
            else:
                break
            continue

        if trainer.is_player_turn():
            # Player's turn
            print(f"Current line: {trainer.get_current_line()}")
            print("Your turn to move!")

            move = input("Enter your move: ").strip()

            if move == 'quit':
                print("\nThanks for practicing!")
                break
            elif move == 'reset':
                trainer.reset()
                print("\nPosition reset!\n")
                trainer.display_board()
                continue
            elif move == 'line':
                print(f"\nCurrent line: {trainer.get_current_line()}\n")
                continue
            elif move == 'board':
                trainer.display_board()
                continue

            is_correct, message = trainer.check_player_move(move)

            if is_correct:
                print(f"{message}")
                trainer.display_board()
            else:
                print(f"{message}")
                retry = input("\nTry again? (yes/no): ").strip().lower()
                if retry in ['yes', 'y']:
                    continue
                else:
                    print("\nStarting over...")
                    trainer.reset()
                    trainer.display_board()
        else:
            # Computer's turn
            computer_move = trainer.make_computer_move()
            if computer_move:
                print(f"\nComputer plays: {computer_move}")
                print(f"Current line: {trainer.get_current_line()}")
                trainer.display_board()
            else:
                print("\nNo more moves available in this line!")
                trainer.reset()
                print("Position reset!\n")
                trainer.display_board()


if __name__ == "__main__":
    main()