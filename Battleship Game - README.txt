BATTLESHIP GAME - README

Overview

This is a console-based Battleship game implemented in Python. It supports:
•	Local multiplayer (2 players on same computer)
•	Single-player vs AI with Easy, Medium, and Hard difficulty levels
•	20x20 game board with ship placement validation
•	Two missile types: Regular (single cell) and Quad (entire row or column)
•	Undo functionality (one undo per player per game)
•	Game timer (8 minutes)
•	Score tracking and winner display

HOW TO RUN

1. Ensure Python 3.x is installed on your system.
2. Download the `battleship.py` file.
3. Run the game from the terminal/command prompt:
python battleship.py
4. Follow on-screen instructions to:
•	Select game mode (vs AI or local multiplayer)
•	Select AI difficulty if applicable
•	Place your ships on the board
•	Take turns attacking opponent’s board using missiles
•	Optionally undo a move once per game
•	Play until all ships are sunk or timer expires

CONTROLS
•	Input coordinates as row and column numbers separated by space (e.g., `5 7`)
•	Choose missile type by entering `R` for regular or `Q` for quad missile
•	For quad missile, choose whether to attack a row or column when prompted


FEATURES
•	Validates ship placement to avoid overlaps and out-of-bounds errors
•	Adaptive AI strategies for challenging gameplay
•	Real-time score updates and board display
•	Undo last move once per player
•	Timer adds urgency to gameplay
•	Multiple missile options
•	Hit/Miss detection

DEPENDENCIES
•	Standard Python 3 libraries only; no external packages required

KNOWN ISSUES
•	Input validation is basic; please enter inputs as requested
•	No network multiplayer support (local play only)

AUTHOR
•	Best Abalaka
•	1st May, 2025

Enjoy the game!
