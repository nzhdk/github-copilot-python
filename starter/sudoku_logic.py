import copy
import random

SIZE = 9
EMPTY = 0

DIFFICULTY_LEVELS = {
    'easy': 46,
    'medium': 36,
    'hard': 26,
}


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def find_hint_cell(puzzle, board, hinted_cells=None):
    """Return the first eligible empty cell, or None when none remain."""
    hinted_cells = hinted_cells or set()
    for row in range(SIZE):
        for col in range(SIZE):
            if (
                puzzle[row][col] == EMPTY
                and board[row][col] == EMPTY
                and (row, col) not in hinted_cells
            ):
                return row, col
    return None


def is_safe(board, row, col, num):
    # Check row and column
    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False
    # Check 3x3 box
    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True


def _board_is_valid(board):
    for row in range(SIZE):
        for col in range(SIZE):
            value = board[row][col]
            if value == EMPTY:
                continue
            for x in range(SIZE):
                if x != col and board[row][x] == value:
                    return False
            for y in range(SIZE):
                if y != row and board[y][col] == value:
                    return False
            start_row = row - row % 3
            start_col = col - col % 3
            for r in range(start_row, start_row + 3):
                for c in range(start_col, start_col + 3):
                    if (r != row or c != col) and board[r][c] == value:
                        return False
    return True


def find_best_empty_cell(board):
    best_cell = None
    best_candidates = None

    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] != EMPTY:
                continue
            candidates = []
            for num in range(1, SIZE + 1):
                if is_safe(board, row, col, num):
                    candidates.append(num)
            if not candidates:
                return None, None
            if best_candidates is None or len(candidates) < len(best_candidates):
                best_cell = (row, col)
                best_candidates = candidates
                if len(best_candidates) == 1:
                    return best_cell, best_candidates

    return best_cell, best_candidates


def count_solutions(board, limit=2):
    """Return the number of valid Sudoku solutions up to the given limit."""
    if limit <= 0:
        return 0

    working_board = deep_copy(board)
    if not _board_is_valid(working_board):
        return 0

    solution_count = 0

    def backtrack():
        nonlocal solution_count
        if solution_count >= limit:
            return

        best_cell, candidates = find_best_empty_cell(working_board)
        if best_cell is None:
            solution_count += 1
            return

        row, col = best_cell
        for num in candidates:
            working_board[row][col] = num
            backtrack()
            working_board[row][col] = EMPTY
            if solution_count >= limit:
                return

    backtrack()
    return solution_count


def fill_board(board):
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def remove_cells(board, clues):
    attempts = SIZE * SIZE - clues
    positions = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(positions)

    while attempts > 0:
        removed = False
        for row, col in positions:
            if board[row][col] == EMPTY:
                continue

            original_value = board[row][col]
            board[row][col] = EMPTY
            if count_solutions(board, limit=2) == 1:
                attempts -= 1
                removed = True
                break
            board[row][col] = original_value

        if not removed:
            break


def generate_puzzle(clues=35):
    board = create_empty_board()
    if not fill_board(board):
        raise ValueError("Unable to generate a valid Sudoku board")

    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)

    if count_solutions(puzzle, limit=2) != 1:
        raise ValueError("Generated puzzle is not uniquely solvable")

    return puzzle, solution


def generate_puzzle_with_difficulty(difficulty='medium'):
    """
    Generate a Sudoku puzzle with the specified difficulty level.
    
    Args:
        difficulty: One of 'easy', 'medium', or 'hard'.
                   Defaults to 'medium'.
    
    Returns:
        A tuple (puzzle, solution) where puzzle is the starting puzzle
        and solution is the completed board.
    
    Raises:
        ValueError: If difficulty is not recognized.
    """
    if difficulty not in DIFFICULTY_LEVELS:
        raise ValueError(
            f"Invalid difficulty '{difficulty}'. Must be one of: {', '.join(DIFFICULTY_LEVELS.keys())}"
        )
    
    clues = DIFFICULTY_LEVELS[difficulty]
    return generate_puzzle(clues=clues)
