from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None,
    'hint_count': 0,
    'hinted_cells': set()
}


def _reset_game_state(puzzle, solution, difficulty):
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    CURRENT['difficulty'] = difficulty
    CURRENT['hint_count'] = 0
    CURRENT['hinted_cells'] = set()


def _is_valid_board(board):
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        return False
    return all(
        isinstance(row, list)
        and len(row) == sudoku_logic.SIZE
        and all(
            isinstance(value, int)
            and not isinstance(value, bool)
            and 0 <= value <= sudoku_logic.SIZE
            for value in row
        )
        for row in board
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    # Support both 'difficulty' (new) and 'clues' (legacy) parameters
    # If 'clues' is provided, use it (backward compatibility)
    # Otherwise, use 'difficulty' and default to 'medium'
    clues_param = request.args.get('clues')
    
    if clues_param is not None:
        # Legacy API: clues parameter takes precedence
        clues = int(clues_param)
        puzzle, solution = sudoku_logic.generate_puzzle(clues)
        _reset_game_state(puzzle, solution, None)  # No difficulty for legacy games
        return jsonify({'puzzle': puzzle})
    
    # New API: use difficulty parameter
    difficulty = request.args.get('difficulty', 'medium')
    
    # Validate difficulty
    if difficulty not in sudoku_logic.DIFFICULTY_LEVELS:
        return jsonify({'error': f"Invalid difficulty. Must be one of: {', '.join(sudoku_logic.DIFFICULTY_LEVELS.keys())}"}), 400
    
    puzzle, solution = sudoku_logic.generate_puzzle_with_difficulty(difficulty)
    clue_count = sudoku_logic.DIFFICULTY_LEVELS[difficulty]

    _reset_game_state(puzzle, solution, difficulty)
    
    return jsonify({
        'puzzle': puzzle,
        'difficulty': difficulty,
        'clue_count': clue_count
    })


@app.route('/hint', methods=['POST'])
def provide_hint():
    puzzle = CURRENT.get('puzzle')
    solution = CURRENT.get('solution')
    if puzzle is None or solution is None:
        return jsonify({'error': 'No game in progress'}), 400

    data = request.get_json(silent=True) or {}
    board = data.get('board')
    if not _is_valid_board(board):
        return jsonify({'error': 'Board must be a valid 9x9 grid of values from 0 to 9'}), 400

    cell = sudoku_logic.find_hint_cell(
        puzzle,
        board,
        CURRENT.get('hinted_cells', set())
    )
    if cell is None:
        return jsonify({
            'message': 'No empty cells remain for a hint',
            'hint_count': CURRENT['hint_count']
        })

    row, col = cell
    CURRENT['hinted_cells'].add(cell)
    CURRENT['hint_count'] += 1
    return jsonify({
        'row': row,
        'col': col,
        'value': solution[row][col],
        'hint_count': CURRENT['hint_count']
    })

@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)