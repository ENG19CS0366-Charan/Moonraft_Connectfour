import numpy as np
import random
import sys
import math

BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)

ROW_COUNT = 6
COLUMN_COUNT = 7

PLAYER = 0
AI = 1

EMPTY = 0
PLAYER_PIECE = 1
AI_PIECE = 2

WINDOW_LENGTH = 4

def create_board():
    board = np.zeros((ROW_COUNT, COLUMN_COUNT), dtype=int)
    return board

def drop_piece(board, row, col, piece):
    board[row][col] = piece

def is_valid_location(board, col):
    return board[ROW_COUNT-1][col] == 0

def get_next_open_row(board, col):
    for r in range(ROW_COUNT):
        if board[r][col] == 0:
            return r

def print_board(board, winning_positions=None):
    for r in range(ROW_COUNT - 1, -1, -1):
        for c in range(COLUMN_COUNT):
            cell = board[r][c]
            if cell == PLAYER_PIECE:
                symbol = "❌"
            elif cell == AI_PIECE:
                symbol = "🔵"
            else:
                symbol = "──"

            if winning_positions and (r, c) in winning_positions:
                symbol = "😍"

            print(symbol, end=" ")
        print()

def winning_move(board, piece):
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT):
            if all(board[r][c + i] == piece for i in range(4)):
                return True
            
    for c in range(COLUMN_COUNT):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c] == piece for i in range(4)):
                return True
            
    for c in range(COLUMN_COUNT - 3):
        for r in range(ROW_COUNT - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    for c in range(COLUMN_COUNT - 3):
        for r in range(3, ROW_COUNT):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True

def is_terminal_node(board):
    return winning_move(board, PLAYER_PIECE) or winning_move(board, AI_PIECE) or len(get_valid_locations(board)) == 0

def get_valid_locations(board):
    valid_locations = []
    for col in range(COLUMN_COUNT):
        if is_valid_location(board, col):
            valid_locations.append(col)
    return valid_locations

def minimax(board, depth, alpha, beta, maximizingPlayer):
    valid_locations = get_valid_locations(board)
    is_terminal = is_terminal_node(board)
    if depth == 0 or is_terminal:
        if is_terminal:
            if winning_move(board, AI_PIECE):
                return (None, 100000000000000)
            elif winning_move(board, PLAYER_PIECE):
                return (None, -10000000000000)
            else:
                return (None, 0)
        else:
            return (None, score_position(board, AI_PIECE))
    if maximizingPlayer:
        value = -math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, AI_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, False)[1]
            if new_score > value:
                value = new_score
                column = col
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return column, value
    else:
        value = math.inf
        column = random.choice(valid_locations)
        for col in valid_locations:
            row = get_next_open_row(board, col)
            b_copy = board.copy()
            drop_piece(b_copy, row, col, PLAYER_PIECE)
            new_score = minimax(b_copy, depth - 1, alpha, beta, True)[1]
            if new_score < value:
                value = new_score
                column = col
            beta = min(beta, value)
            if alpha >= beta:
                break
        return column, value

def pick_best_move(board, piece):
    valid_locations = get_valid_locations(board)
    best_score = -10000
    best_col = random.choice(valid_locations)
    for col in valid_locations:
        row = get_next_open_row(board, col)
        temp_board = board.copy()
        drop_piece(temp_board, row, col, piece)
        score = score_position(temp_board, piece)
        if score > best_score:
            best_score = score
            best_col = col
    return best_col

def score_position(board, piece):
    score = 0

    center_array = [int(i) for i in list(board[:, COLUMN_COUNT//2])]
    center_count = center_array.count(piece)
    score += center_count * 3

    for r in range(ROW_COUNT):
        row_array = [int(i) for i in list(board[r, :])]
        for c in range(COLUMN_COUNT - 3):
            window = row_array[c:c+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for c in range(COLUMN_COUNT):
        col_array = [int(i) for i in list(board[:, c])]
        for r in range(ROW_COUNT - 3):
            window = col_array[r:r+WINDOW_LENGTH]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    for r in range(ROW_COUNT - 3):
        for c in range(COLUMN_COUNT - 3):
            window = [board[r+3-i][c+i] for i in range(WINDOW_LENGTH)]
            score += evaluate_window(window, piece)

    return score

def evaluate_window(window, piece):
    score = 0
    opp_piece = PLAYER_PIECE if piece == AI_PIECE else AI_PIECE

    if window.count(piece) == 4:
        score += 100
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += 5
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += 2

    if window.count(opp_piece) == 3 and window.count(EMPTY) == 1:
        score -= 4

    return score

def find_winning_positions(board, piece):
    winning_positions = []
    for r in range(ROW_COUNT):
        for c in range(COLUMN_COUNT):
            if board[r][c] == piece:
                if c <= COLUMN_COUNT - 4 and all(board[r][c+i] == piece for i in range(4)):
                    winning_positions.extend([(r, c+i) for i in range(4)])

                if r <= ROW_COUNT - 4 and all(board[r+i][c] == piece for i in range(4)):
                    winning_positions.extend([(r+i, c) for i in range(4)])

                if c <= COLUMN_COUNT - 4 and r <= ROW_COUNT - 4 and all(board[r+i][c+i] == piece for i in range(4)):
                    winning_positions.extend([(r+i, c+i) for i in range(4)])

                if c <= COLUMN_COUNT - 4 and r >= 3 and all(board[r-i][c+i] == piece for i in range(4)):
                    winning_positions.extend([(r-i, c+i) for i in range(4)])

    return winning_positions

def main():
    board = create_board()
    print_board(board)
    game_over = False

    difficulty = input("Choose a difficulty level (easy, medium, hard): ").lower()

    if difficulty not in ["easy", "medium", "hard"]:
        print("Invalid difficulty level. Please choose from 'easy', 'medium', or 'hard'.")
        return

    if difficulty == "easy":
        max_depth = 1
    elif difficulty == "medium":
        max_depth = 3
    elif difficulty == "hard":
        max_depth = 5

    turn = random.randint(PLAYER, AI)

    while not game_over:
        if turn == PLAYER:
            print()
            col = int(input("Player's turn (1-7): "))
            col -= 1
            print()
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, PLAYER_PIECE)

                winning_positions = find_winning_positions(board, PLAYER_PIECE)
                print_board(board, winning_positions)

                if winning_move(board, PLAYER_PIECE):
                    print("Player 1 wins!!")
                    game_over = True

                turn += 1
                turn %= 2
                
                print()
                print("Player's input: ")
                print()



        elif turn == AI and not game_over:
            col, _ = minimax(board, 5, -math.inf, math.inf, True)
            if is_valid_location(board, col):
                row = get_next_open_row(board, col)
                drop_piece(board, row, col, AI_PIECE)

                winning_positions = find_winning_positions(board, AI_PIECE)
                print_board(board, winning_positions)

                if winning_move(board, AI_PIECE):
                    print()
                    print("Player 2 wins!!")
                    print()
                    game_over = True

                turn += 1
                turn %= 2

    if game_over:
        print("H u r r a y   G a m e   o v e r !")
        print()


if __name__ == "__main__":
    main()
