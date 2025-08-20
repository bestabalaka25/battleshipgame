import random
import time
import copy
from collections import deque


GRID_SIZE = 20  # Size of the board (20x20)
SHIP_SIZES = [5, 4, 3, 3, 2]  # Sizes of ships to place
EMPTY_CELL = '~'  # Symbol for empty water
SHIP_CELL = 'S'   # Symbol for ship
HIT_CELL = 'X'    # Symbol for hit ship
MISS_CELL = 'O'   # Symbol for missed shot

class Board:
    def __init__(self):
        # Initialize a GRID_SIZE x GRID_SIZE grid filled with EMPTY_CELL
        self.grid = [[EMPTY_CELL for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.ships = []  # List of ships, each ship is a list of coordinates
        self.ship_cells = set()  # Set of all ship coordinates for quick lookup

    def place_ship(self, size, row, col, horizontal):
        coords = []
        if horizontal:
            # Check if ship fits horizontally
            if col + size > GRID_SIZE:
                return False
            # Check for overlap
            for c in range(col, col + size):
                if self.grid[row][c] != EMPTY_CELL:
                    return False
                coords.append((row, c))
        else:
            # Check if ship fits vertically
            if row + size > GRID_SIZE:
                return False
            # Check for overlap
            for r in range(row, row + size):
                if self.grid[r][col] != EMPTY_CELL:
                    return False
                coords.append((r, col))
        # Place ship on grid
        for r, c in coords:
            self.grid[r][c] = SHIP_CELL
        self.ships.append(coords)
        self.ship_cells.update(coords)
        return True

    def receive_attack(self, row, col):
        cell = self.grid[row][col]
        if cell == SHIP_CELL:
            self.grid[row][col] = HIT_CELL
            self.ship_cells.remove((row, col))
            return "Hit!"
        elif cell == EMPTY_CELL:
            self.grid[row][col] = MISS_CELL
            return "Miss!"
        elif cell in (HIT_CELL, MISS_CELL):
            return "Already"
        else:
            return "Error"

    def all_ships_sunk(self):
        return len(self.ship_cells) == 0

    def display(self, hide_ships=True):
        print("   " + " ".join(f"{i:2}" for i in range(GRID_SIZE)))
        for i, row in enumerate(self.grid):
            display_row = []
            for cell in row:
                if hide_ships and cell == SHIP_CELL:
                    display_row.append(EMPTY_CELL)
                else:
                    display_row.append(cell)
            print(f"{i:2} " + " ".join(display_row))

    def copy(self):
        new_board = Board()
        new_board.grid = copy.deepcopy(self.grid)
        new_board.ships = copy.deepcopy(self.ships)
        new_board.ship_cells = set(self.ship_cells)
        return new_board

class Player:
    def __init__(self, name, is_ai=False, ai_level='Easy'):
        self.name = name
        self.board = Board()
        self.is_ai = is_ai
        self.ai_level = ai_level
        self.score = 0  # Number of hits scored
        self.undo_used = False  # Tracks if undo has been used
        self.missiles = {'regular': 30, 'quad': 2}  # Missile counts
        self.hit_stack = deque()  # For Hard AI: stack of target coordinates
        self.possible_targets = set((r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE))
        self.last_hit = None  # Last successful hit coordinate for AI

    def place_ships_randomly(self):
        #Automatically places all ships randomly on the board.
        for size in SHIP_SIZES:
            placed = False
            while not placed:
                horizontal = random.choice([True, False])
                row = random.randint(0, GRID_SIZE - (1 if horizontal else size))
                col = random.randint(0, GRID_SIZE - (size if horizontal else 1))
                placed = self.board.place_ship(size, row, col, horizontal)

    def place_ships_manually(self):
        print(f"{self.name}, place your ships on the {GRID_SIZE}x{GRID_SIZE} board.")
        self.board.display(hide_ships=False)

        # Asks if player wants automatic placement
        auto_place = input("Do you want to place ships automatically? (Y/N): ").strip().upper()
        if auto_place == "Y":
            self.place_ships_randomly()
            self.board.display(hide_ships=False)
            return

        # Manual placement for each ship size
        for size in SHIP_SIZES:
            placed = False
            while not placed:
                print(f"Place ship of size {size}")
                try:
                    inp = input("Enter row,col and orientation (H/V) separated by spaces (e.g. 3 4 H): ")
                    row, col, orient = inp.strip().split()
                    row, col = int(row), int(col)
                    horizontal = orient.upper() == 'H'
                    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                        placed = self.board.place_ship(size, row, col, horizontal)
                        if not placed:
                            print("Invalid placement (overlap or out of bounds). Try again.")
                        else:
                            self.board.display(hide_ships=False)
                    else:
                        print("Coordinates out of bounds. Try again.")
                except Exception:
                    print("Invalid input format. Try again.")

    def get_move(self, opponent_board):
        while True:
            print(f"{self.name}'s turn. Missiles left: Regular={self.missiles['regular']}, Quad={self.missiles['quad']}")
            missile_type = input("Choose missile type (R for regular, Q for quad): ").strip().upper()
            if missile_type not in ('R', 'Q'):
                print("Invalid missile type. Choose R or Q.")
                continue
            if missile_type == 'R' and self.missiles['regular'] <= 0:
                print("No regular missiles left.")
                continue
            if missile_type == 'Q' and self.missiles['quad'] <= 0:
                print("No quad missiles left.")
                continue

            try:
                inp = input("Enter target row and column separated by space (e.g. 5 7): ")
                row, col = map(int, inp.strip().split())
                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                    return missile_type, row, col
                else:
                    print("Coordinates out of bounds. Try again.")
            except:
                print("Invalid input format. Try again.")

    def ai_move(self, opponent_board):
        if self.ai_level == 'Easy':
            missile_type = 'R' if self.missiles['regular'] > 0 else 'Q'
            if missile_type == 'Q' and self.missiles['quad'] <= 0:
                missile_type = 'R'
            target = random.choice(list(self.possible_targets))
            return missile_type, target[0], target[1]
        elif self.ai_level == 'Medium':
            if self.last_hit:
                r, c = self.last_hit
                adjacents = [(r-1,c),(r+1,c),(r,c-1),(r,c+1)]
                random.shuffle(adjacents)
                for nr, nc in adjacents:
                    if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE and (nr,nc) in self.possible_targets:
                        missile_type = 'R' if self.missiles['regular'] > 0 else 'Q'
                        return missile_type, nr, nc
            missile_type = 'R' if self.missiles['regular'] > 0 else 'Q'
            target = random.choice(list(self.possible_targets))
            return missile_type, target[0], target[1]
        else:  # Hard AI
            while self.hit_stack:
                target = self.hit_stack.pop()
                if target in self.possible_targets:
                    missile_type = 'R' if self.missiles['regular'] > 0 else 'Q'
                    return missile_type, target[0], target[1]
            missile_type = 'R' if self.missiles['regular'] > 0 else 'Q'
            target = random.choice(list(self.possible_targets))
            return missile_type, target[0], target[1]

    def update_ai_after_hit(self, row, col, hit):
        if not self.is_ai:
            return
        if hit:
            self.last_hit = (row, col)
            if self.ai_level == 'Hard':
                adjacents = [(row-1,col),(row+1,col),(row,col-1),(row,col+1)]
                for nr, nc in adjacents:
                    if 0 <= nr < GRID_SIZE and 0 <= nc < GRID_SIZE:
                        self.hit_stack.append((nr, nc))

class BattleshipGame:
    def __init__(self):
        self.players = []
        self.turn = 0  # Turn counter to alternate players
        self.move_history = []  # Stack for undo functionality
        self.start_time = None
        self.time_limit = 20 * 60  # 20 minutes timer
        self.mode = None  # Game mode: vs AI or local multiplayer

    def select_mode(self):
        print("Welcome To Best's Battleship Game:")
        print("Please Select Mode:")
        print("1) vs AI")
        print("2) Local Multiplayer")
        while True:
            m = input("Mode? ").strip()
            if m in ('1', '2'):
                self.mode = int(m)
                break
            else:
                print("Invalid input. Choose 1 or 2.")

    @staticmethod
    def select_difficulty():
        print("Select AI Difficulty Level:")
        print("1) Easy")
        print("2) Medium")
        print("3) Hard")
        while True:
            d = input("Difficulty? ").strip()
            if d in ('1', '2', '3'):
                return {'1': 'Easy', '2': 'Medium', '3': 'Hard'}[d]
            else:
                print("Invalid input. Choose 1, 2 or 3.")

    def setup_players(self):
        if self.mode == 1:
            difficulty = self.select_difficulty()
            p1 = Player("Player 1", is_ai=False)
            p2 = Player("Computer", is_ai=True, ai_level=difficulty)
            self.players = [p1, p2]
            p1.place_ships_manually()
            p2.place_ships_randomly()
        else:
            p1 = Player("Player 1", is_ai=False)
            p2 = Player("Player 2", is_ai=False)
            self.players = [p1, p2]
            p1.place_ships_manually()
            p2.place_ships_manually()

    def print_scores(self):
        print(f"Scores: {self.players[0].name}: {self.players[0].score} | {self.players[1].name}: {self.players[1].score}")

    def undo_move(self, player_idx):
        if not self.move_history:
            print("No moves to undo.")
            return False
        last_move = self.move_history.pop()
        _, board_copies, missile_copies, score_copies = last_move
        player = self.players[player_idx]
        if player.undo_used:
            print("You have already used your undo this match.")
            return False
        # Restore boards
        self.players[0].board = board_copies[0].copy()
        self.players[1].board = board_copies[1].copy()
        # Restore missile counts
        self.players[0].missiles = missile_copies[0].copy()
        self.players[1].missiles = missile_copies[1].copy()
        # Restore scores
        self.players[0].score = score_copies[0]
        self.players[1].score = score_copies[1]
        player.undo_used = True
        print(f"{player.name} undid their last move.")
        return True

    def apply_missile(self, missile_type, row, col, attacker_idx, defender_idx):
        attacker = self.players[attacker_idx]
        defender = self.players[defender_idx]
        hits = 0
        coords_to_attack = []

        if missile_type == 'R':
            coords_to_attack = [(row, col)]
            attacker.missiles['regular'] -= 1
        else:
            # Quad missile: ask human player for row or column; AI chooses randomly on its own
            if attacker.is_ai:
                choice = random.choice(['row', 'col'])
            else:
                while True:
                    choice = input("Quad missile: Attack entire row or column? (R/C): ").strip().upper()
                    if choice in ('R', 'C'):
                        choice = 'row' if choice == 'R' else 'col'
                        break
                    else:
                        print("Invalid choice. Enter R or C.")
            attacker.missiles['quad'] -= 1
            if choice == 'row':
                coords_to_attack = [(row, c) for c in range(GRID_SIZE)]
            else:
                coords_to_attack = [(r, col) for r in range(GRID_SIZE)]

        # Apply attacks to all targeted cells
        for r, c in coords_to_attack:
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                result = defender.board.receive_attack(r, c)
                if result == "Hit!":
                    hits += 1
                    attacker.score += 1
                    attacker.update_ai_after_hit(r, c, True)
                elif result == "Miss!":
                    attacker.update_ai_after_hit(r, c, False)
        return hits

    def check_winner(self):
        for i, player in enumerate(self.players):
            if player.board.all_ships_sunk():
                return 1 - i  # Opponent wins
        return None

    def start_timer(self):
        #Starts the game timer.
        self.start_time = time.time()

    def time_remaining(self):
        #Returns remaining time in seconds
        elapsed = time.time() - self.start_time
        remaining = self.time_limit - elapsed
        return max(0, remaining)

    def both_players_out_of_missiles(self):
        #Returns True if both players are out of missiles.
        return all(out_of_missiles(p) for p in self.players)

    def run(self):
        self.select_mode()
        self.setup_players()
        self.start_timer()

        while True:
            current_player_idx = self.turn % 2
            opponent_idx = 1 - current_player_idx
            current_player = self.players[current_player_idx]
            opponent = self.players[opponent_idx]

            print(f"\n{current_player.name}'s turn.")
            print(f"Time remaining: {int(self.time_remaining())} seconds")
            print(f"{current_player.name}'s board:")
            current_player.board.display(hide_ships=False)
            print(f"{opponent.name}'s board:")
            opponent.board.display(hide_ships=True)
            self.print_scores()

            # Check if current player is out of missiles
            if out_of_missiles(current_player):
                print(f"{current_player.name} is out of missiles!")
                if self.both_players_out_of_missiles():
                    print("Both players are out of missiles!")
                    # Decide winner by score or tie
                    if self.players[0].score > self.players[1].score:
                        print(f"{self.players[0].name} wins by score!")
                    elif self.players[1].score > self.players[0].score:
                        print(f"{self.players[1].name} wins by score!")
                    else:
                        print("It's a tie!")
                    self.print_scores()
                    break
                else:
                    print(f"{opponent.name} still has missiles, they may continue.")
                    self.turn += 1
                    continue

            # Save state for undo: boards, missiles, scores
            board_copies = [p.board.copy() for p in self.players]
            missile_copies = [p.missiles.copy() for p in self.players]
            score_copies = [p.score for p in self.players]
            self.move_history.append((current_player_idx, board_copies, missile_copies, score_copies))

            # Undo option: ask only human players who haven't used undo
            if not current_player.is_ai and not current_player.undo_used:
                undo_choice = input("Do you want to undo the last move? (Y/N): ").strip().upper()
                if undo_choice == 'Y':
                    if self.undo_move(current_player_idx):
                        self.turn -= 1
                        continue

            # Get move from AI or human
            if current_player.is_ai:
                missile_type, row, col = current_player.ai_move(opponent.board)
                print(f"AI chose missile {missile_type} at ({row},{col})")
            else:
                missile_type, row, col = current_player.get_move(opponent.board)

            # Remove targeted cell from AI possible targets
            if current_player.is_ai and (row, col) in current_player.possible_targets:
                current_player.possible_targets.remove((row, col))

            # Apply missile attack and count hits
            hits = self.apply_missile(missile_type, row, col, current_player_idx, opponent_idx)
            print(f"{current_player.name} scored {hits} hits this turn.")

            # AI automatic undo once per game if it misses
            if current_player.is_ai and not current_player.undo_used and hits == 0:
                print(f"AI is undoing its last move automatically (missed and hasn't undone yet).")
                if self.undo_move(current_player_idx):
                    self.turn -= 1
                    continue

            # Check for winner by sinking all ships
            winner = self.check_winner()
            if winner is not None:
                print(f"\nGame Over! {self.players[winner].name} wins!")
                self.print_scores()
                break

            # Check for timer expiry
            if self.time_remaining() <= 0:
                print("\nTime's up!")
                # Decide winner by score or tie
                if self.players[0].score > self.players[1].score:
                    print(f"{self.players[0].name} wins by score!")
                elif self.players[1].score > self.players[0].score:
                    print(f"{self.players[1].name} wins by score!")
                else:
                    print("It's a tie!")
                self.print_scores()
                break

            self.turn += 1


def out_of_missiles(player):
    #Returns True if player has no missiles left.
    return player.missiles['regular'] <= 0 and player.missiles['quad'] <= 0


if __name__ == "__main__":
    game = BattleshipGame()
    game.run()
