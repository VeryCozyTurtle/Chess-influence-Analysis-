import chess
import chess.pgn
import numpy as np
import matplotlib.pyplot as plt
import os

# Function to parse PGN file and extract moves
def parse_pgn(file_path):
    with open(file_path, 'r') as pgn_file:
        game = chess.pgn.read_game(pgn_file)
    return game

# Function to calculate square ownership and influence
def calculate_influence(board, depth=3):
    influence = np.zeros((8, 8, 2))  # 2 channels for White and Black
    
    def add_influence(square, weight, color):
        row, col = divmod(square, 8)
        influence[row, col, 0 if color else 1] += weight

    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            color = piece.color
            moves = board.attacks(square)
            for move in moves:
                add_influence(move, 1.0, color)  # First-order influence

            # Simulate second and third-order influences
            if depth > 1:
                for move in moves:
                    board.push(chess.Move(square, move))
                    second_moves = board.attacks(move)
                    for second_move in second_moves:
                        add_influence(second_move, 0.65, color)  # Second-order influence

                    if depth > 2:
                        for second_move in second_moves:
                            board.push(chess.Move(move, second_move))
                            third_moves = board.attacks(second_move)
                            for third_move in third_moves:
                                add_influence(third_move, 0.2, color)  # Third-order influence
                            board.pop()
                    board.pop()
    return influence

# Function to visualize and save influence maps as PNG images
def save_influence_maps(influence_maps, boards, output_dir="computed_game"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        # Clear the directory if it already exists
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)

    piece_symbols = {
        chess.PAWN: "P", chess.KNIGHT: "N", chess.BISHOP: "B",
        chess.ROOK: "R", chess.QUEEN: "Q", chess.KING: "K"
    }

    for i, (influence, board) in enumerate(zip(influence_maps, boards)):
        plt.figure(figsize=(8, 8))
        
        # Create a base grid with custom colors
        grid_colors = np.zeros((8, 8, 3))  # RGB grid
        
        # Calculate ownership colors
        white_control = influence[:, :, 0]
        black_control = influence[:, :, 1]
        
        for row in range(8):
            for col in range(8):
                total_control = white_control[row, col] + black_control[row, col]
                if total_control == 0:
                    grid_colors[row, col] = [0.0, 0.0, 1.0]  # Blue (unowned)
                else:
                    # Calculate the gradient color based on control
                    white_ratio = white_control[row, col] / total_control
                    black_ratio = black_control[row, col] / total_control
                    grid_colors[row, col] = [
                        white_ratio,
                        white_ratio,
                        black_ratio
                    ]  # Gradation from white to black

        plt.imshow(grid_colors[::-1], interpolation="nearest")  # Flip vertically to match chessboard orientation
        
        # Add pieces to the board visualization
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                row, col = divmod(square, 8)  # Use original square index
                symbol = piece_symbols[piece.piece_type]
                symbol_color = "white" if piece.color == chess.WHITE else "black"
                plt.text(col, 7.5 - row - 0.5, symbol,
                         ha="center", va="center", fontsize=20,
                         color=symbol_color)

        plt.title(f"Board State at Move {i+1}")
        plt.xticks(range(8), ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h'])
        plt.yticks(range(8), ['1', '2', '3', '4', '5', '6', '7', '8'][::-1])
        plt.grid(False)
        
        plt.savefig(os.path.join(output_dir, f"turn_{i+1}.png"))
        plt.close()

# Load PGN file and process moves
pgn_file = "chessanalysis_input.py"
game = parse_pgn(pgn_file)
board = game.board()

# Store influence maps and boards for each move
influence_maps = []
boards = []
for move in game.mainline_moves():
    board.push(move)
    influence = calculate_influence(board)
    influence_maps.append(influence)
    boards.append(board.copy())

# Save influence maps as PNG images
save_influence_maps(influence_maps, boards)

print(f"Analysis complete. {len(influence_maps)} board states have been saved in the 'computed_game' directory.")
