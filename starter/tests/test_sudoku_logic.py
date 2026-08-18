import sys
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[1]
STARTER_DIR = ROOT / "starter"
for path in (str(ROOT), str(STARTER_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

import sudoku_logic


def test_generate_puzzle_has_9x9_structure():
    """The generator should return a valid 9x9 puzzle and solution grid."""
    puzzle, solution = sudoku_logic.generate_puzzle(35)

    assert isinstance(puzzle, list)
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert all(isinstance(value, int) for row in puzzle for value in row)

    assert isinstance(solution, list)
    assert len(solution) == 9
    assert all(len(row) == 9 for row in solution)
    assert all(isinstance(value, int) for row in solution for value in row)


def test_generated_solution_is_valid_sudoku():
    """The solved board from generate_puzzle must satisfy Sudoku rules."""
    _, solution = sudoku_logic.generate_puzzle(35)

    for row in solution:
        assert sorted(row) == list(range(1, 10))

    for col_index in range(sudoku_logic.SIZE):
        column = [solution[row_index][col_index] for row_index in range(sudoku_logic.SIZE)]
        assert sorted(column) == list(range(1, 10))

    for start_row in range(0, sudoku_logic.SIZE, 3):
        for start_col in range(0, sudoku_logic.SIZE, 3):
            box = [
                solution[row][col]
                for row in range(start_row, start_row + 3)
                for col in range(start_col, start_col + 3)
            ]
            assert sorted(box) == list(range(1, 10))


def test_requested_clue_count_is_respected():
    """The puzzle should keep the requested number of starting clues."""
    clues = 30
    puzzle, _ = sudoku_logic.generate_puzzle(clues)

    filled_cells = sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row)
    assert filled_cells == clues


def test_is_safe_detects_row_conflict():
    """is_safe should reject duplicate values in the same row."""
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[0][1] = 2
    board[0][2] = 3
    board[0][3] = 4
    board[0][4] = 5
    board[0][5] = 6
    board[0][6] = 7
    board[0][7] = 8

    assert sudoku_logic.is_safe(board, 0, 8, 1) is False
    assert sudoku_logic.is_safe(board, 0, 8, 9) is True


def test_is_safe_detects_column_conflict():
    """is_safe should reject duplicate values in the same column."""
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[1][0] = 2
    board[2][0] = 3
    board[3][0] = 4
    board[4][0] = 5
    board[5][0] = 6
    board[6][0] = 7
    board[7][0] = 8

    assert sudoku_logic.is_safe(board, 8, 0, 1) is False
    assert sudoku_logic.is_safe(board, 8, 0, 9) is True


def test_is_safe_detects_3x3_box_conflict():
    """is_safe should reject duplicate values within the same 3x3 box."""
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1

    assert sudoku_logic.is_safe(board, 1, 1, 1) is False
    assert sudoku_logic.is_safe(board, 1, 1, 2) is True


def test_count_solutions_for_valid_completed_board_is_one():
    """A valid solved board should have exactly one solution."""
    board = [
        [5, 3, 4, 6, 7, 8, 9, 1, 2],
        [6, 7, 2, 1, 9, 5, 3, 4, 8],
        [1, 9, 8, 3, 4, 2, 5, 6, 7],
        [8, 5, 9, 7, 6, 1, 4, 2, 3],
        [4, 2, 6, 8, 5, 3, 7, 9, 1],
        [7, 1, 3, 9, 2, 4, 8, 5, 6],
        [9, 6, 1, 5, 3, 7, 2, 8, 4],
        [2, 8, 7, 4, 1, 9, 6, 3, 5],
        [3, 4, 5, 2, 8, 6, 1, 7, 9],
    ]

    assert sudoku_logic.count_solutions(board, limit=2) == 1


def test_count_solutions_for_contradictory_board_is_zero():
    """A board with conflicting clues cannot have a valid solution."""
    board = sudoku_logic.create_empty_board()
    board[0][0] = 1
    board[0][1] = 1

    assert sudoku_logic.count_solutions(board, limit=2) == 0


def test_count_solutions_for_under_constrained_board_has_multiple_solutions():
    """An under-constrained board should permit multiple completions."""
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.count_solutions(board, limit=3) > 1


def test_generated_puzzle_has_exactly_one_solution():
    """Generated puzzles should remain uniquely solvable."""
    puzzle, _ = sudoku_logic.generate_puzzle(35)

    assert sudoku_logic.count_solutions(puzzle, limit=2) == 1


def test_generated_puzzle_respects_requested_clue_count():
    """Generated puzzles should keep the requested number of clues when possible."""
    clues = 30
    puzzle, _ = sudoku_logic.generate_puzzle(clues)

    filled_cells = sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row)
    assert filled_cells == clues
    assert sudoku_logic.count_solutions(puzzle, limit=2) == 1


# ===== Difficulty level tests =====

def test_difficulty_levels_are_defined():
    """DIFFICULTY_LEVELS should contain all required difficulty levels."""
    assert 'easy' in sudoku_logic.DIFFICULTY_LEVELS
    assert 'medium' in sudoku_logic.DIFFICULTY_LEVELS
    assert 'hard' in sudoku_logic.DIFFICULTY_LEVELS


def test_difficulty_levels_are_ordered_correctly():
    """Easy should have more clues than Medium, which should have more than Hard."""
    easy_clues = sudoku_logic.DIFFICULTY_LEVELS['easy']
    medium_clues = sudoku_logic.DIFFICULTY_LEVELS['medium']
    hard_clues = sudoku_logic.DIFFICULTY_LEVELS['hard']
    
    assert easy_clues > medium_clues
    assert medium_clues > hard_clues


def test_easy_clues_is_46():
    """Easy difficulty should be configured for 46 clues."""
    assert sudoku_logic.DIFFICULTY_LEVELS['easy'] == 46


def test_medium_clues_is_36():
    """Medium difficulty should be configured for 36 clues."""
    assert sudoku_logic.DIFFICULTY_LEVELS['medium'] == 36


def test_hard_clues_is_26():
    """Hard difficulty should be configured for 26 clues."""
    assert sudoku_logic.DIFFICULTY_LEVELS['hard'] == 26


def test_generate_puzzle_with_difficulty_easy():
    """generate_puzzle_with_difficulty('easy') should create a puzzle with approximately 46 clues."""
    puzzle, solution = sudoku_logic.generate_puzzle_with_difficulty('easy')
    
    filled_cells = sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row)
    # Allow ±1 clue tolerance due to the randomness of cell removal
    assert 45 <= filled_cells <= 47
    assert sudoku_logic.count_solutions(puzzle, limit=2) == 1


def test_generate_puzzle_with_difficulty_medium():
    """generate_puzzle_with_difficulty('medium') should create a puzzle with approximately 36 clues."""
    puzzle, solution = sudoku_logic.generate_puzzle_with_difficulty('medium')
    
    filled_cells = sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row)
    # Allow ±1 clue tolerance due to the randomness of cell removal
    assert 35 <= filled_cells <= 37
    assert sudoku_logic.count_solutions(puzzle, limit=2) == 1


def test_generate_puzzle_with_difficulty_hard():
    """generate_puzzle_with_difficulty('hard') should create a puzzle with approximately 26 clues."""
    puzzle, solution = sudoku_logic.generate_puzzle_with_difficulty('hard')
    
    filled_cells = sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row)
    # Allow ±1 clue tolerance due to the randomness of cell removal
    assert 25 <= filled_cells <= 27
    assert sudoku_logic.count_solutions(puzzle, limit=2) == 1


def test_generate_puzzle_with_difficulty_default_is_medium():
    """generate_puzzle_with_difficulty() without args should default to medium."""
    puzzle, _ = sudoku_logic.generate_puzzle_with_difficulty()
    
    filled_cells = sum(cell != sudoku_logic.EMPTY for row in puzzle for cell in row)
    assert filled_cells == 36


def test_generate_puzzle_with_difficulty_invalid_raises_error():
    """generate_puzzle_with_difficulty() should raise ValueError for invalid difficulty."""
    with pytest.raises(ValueError):
        sudoku_logic.generate_puzzle_with_difficulty('invalid')


def test_find_hint_cell_selects_first_eligible_empty_cell():
    puzzle = sudoku_logic.create_empty_board()
    board = sudoku_logic.create_empty_board()
    puzzle[0][0] = 5
    board[0][1] = 3

    assert sudoku_logic.find_hint_cell(puzzle, board) == (0, 2)


def test_find_hint_cell_skips_previously_hinted_cell():
    puzzle = sudoku_logic.create_empty_board()
    board = sudoku_logic.create_empty_board()

    assert sudoku_logic.find_hint_cell(puzzle, board, {(0, 0)}) == (0, 1)


def test_find_hint_cell_returns_none_when_no_eligible_cells_remain():
    puzzle = sudoku_logic.create_empty_board()
    board = [[1 for _ in range(9)] for _ in range(9)]

    assert sudoku_logic.find_hint_cell(puzzle, board) is None
