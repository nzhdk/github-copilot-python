import copy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STARTER_DIR = ROOT / "starter"
for path in (str(ROOT), str(STARTER_DIR)):
    if path not in sys.path:
        sys.path.insert(0, path)

import app as app_module


def test_get_index_page_returns_html():
    """GET / should render the Sudoku page and game markup."""
    with app_module.app.test_client() as client:
        response = client.get("/")

    assert response.status_code == 200
    html = response.get_data(as_text=True)
    assert "Sudoku Game" in html
    assert "sudoku-board" in html


def test_index_page_contains_scoreboard_markup():
    """The game page should include accessible scoreboard and score-entry markup."""
    with app_module.app.test_client() as client:
        response = client.get("/")

    html = response.get_data(as_text=True)
    assert "Top 10 Fastest Times" in html
    assert 'id="scoreboard-table"' in html
    assert 'id="scoreboard-body"' in html
    assert 'id="score-form"' in html
    assert 'id="player-name"' in html
    assert 'for="player-name"' in html
    assert 'maxlength="30"' in html
    for heading in ("Rank", "Player", "Time", "Difficulty", "Hints"):
        assert heading in html


def test_index_page_contains_accessible_theme_toggle():
    """The game page should expose a visible, stateful theme toggle."""
    with app_module.app.test_client() as client:
        response = client.get("/")

    html = response.get_data(as_text=True)
    assert 'id="theme-toggle"' in html
    assert 'type="button"' in html
    assert 'aria-pressed="false"' in html
    assert 'aria-label="Switch to dark mode"' in html
    assert "Dark mode" in html


def test_get_new_game_returns_9x9_puzzle_json():
    """GET /new should create a puzzle and return a 9x9 JSON board."""
    with app_module.app.test_client() as client:
        response = client.get("/new?clues=35")

    assert response.status_code == 200
    data = response.get_json()
    assert "puzzle" in data

    puzzle = data["puzzle"]
    assert len(puzzle) == 9
    assert all(len(row) == 9 for row in puzzle)
    assert sum(cell != 0 for row in puzzle for cell in row) == 35
    assert app_module.CURRENT["solution"] is not None


def test_post_check_reports_incorrect_cells():
    """POST /check should compare the submitted board with the stored solution."""
    with app_module.app.test_client() as client:
        client.get("/new?clues=35")
        solution = app_module.CURRENT["solution"]
        board = copy.deepcopy(solution)
        board[0][0] = 9 if solution[0][0] != 9 else 1

        response = client.post("/check", json={"board": board})

    assert response.status_code == 200
    data = response.get_json()
    assert [0, 0] in data["incorrect"]


def test_post_check_without_active_game_returns_400():
    """POST /check should fail cleanly when no game has been created."""
    app_module.CURRENT["puzzle"] = None
    app_module.CURRENT["solution"] = None

    with app_module.app.test_client() as client:
        response = client.post("/check", json={"board": [[0 for _ in range(9)] for _ in range(9)]})

    assert response.status_code == 400
    data = response.get_json()
    assert data["error"] == "No game in progress"


# ===== Difficulty level tests =====

def test_new_game_with_easy_difficulty():
    """GET /new?difficulty=easy should return a puzzle with approximately 46 clues and include difficulty in response."""
    with app_module.app.test_client() as client:
        response = client.get("/new?difficulty=easy")

    assert response.status_code == 200
    data = response.get_json()
    assert "puzzle" in data
    assert data["difficulty"] == "easy"
    assert data["clue_count"] == 46
    
    puzzle = data["puzzle"]
    filled_cells = sum(cell != 0 for row in puzzle for cell in row)
    # Allow ±1 clue tolerance due to the randomness of cell removal
    assert 45 <= filled_cells <= 47
    assert app_module.CURRENT["difficulty"] == "easy"


def test_new_game_with_medium_difficulty():
    """GET /new?difficulty=medium should return a puzzle with approximately 36 clues and include difficulty in response."""
    with app_module.app.test_client() as client:
        response = client.get("/new?difficulty=medium")

    assert response.status_code == 200
    data = response.get_json()
    assert "puzzle" in data
    assert data["difficulty"] == "medium"
    assert data["clue_count"] == 36
    
    puzzle = data["puzzle"]
    filled_cells = sum(cell != 0 for row in puzzle for cell in row)
    # Allow ±1 clue tolerance due to the randomness of cell removal
    assert 35 <= filled_cells <= 37
    assert app_module.CURRENT["difficulty"] == "medium"


def test_new_game_with_hard_difficulty():
    """GET /new?difficulty=hard should return a puzzle with approximately 26 clues and include difficulty in response."""
    with app_module.app.test_client() as client:
        response = client.get("/new?difficulty=hard")

    assert response.status_code == 200
    data = response.get_json()
    assert "puzzle" in data
    assert data["difficulty"] == "hard"
    assert data["clue_count"] == 26
    
    puzzle = data["puzzle"]
    filled_cells = sum(cell != 0 for row in puzzle for cell in row)
    # Allow ±1 clue tolerance due to the randomness of cell removal
    assert 25 <= filled_cells <= 27
    assert app_module.CURRENT["difficulty"] == "hard"


def test_new_game_without_difficulty_defaults_to_medium():
    """GET /new without difficulty parameter should default to medium."""
    with app_module.app.test_client() as client:
        response = client.get("/new")

    assert response.status_code == 200
    data = response.get_json()
    assert data["difficulty"] == "medium"
    assert data["clue_count"] == 36
    
    puzzle = data["puzzle"]
    filled_cells = sum(cell != 0 for row in puzzle for cell in row)
    assert filled_cells == 36


def test_new_game_with_invalid_difficulty_returns_400():
    """GET /new?difficulty=invalid should return HTTP 400."""
    with app_module.app.test_client() as client:
        response = client.get("/new?difficulty=expert")

    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Invalid difficulty" in data["error"]


def test_post_hint_without_active_game_returns_400():
    app_module.CURRENT['puzzle'] = None
    app_module.CURRENT['solution'] = None

    with app_module.app.test_client() as client:
        response = client.post('/hint', json={'board': [[0 for _ in range(9)] for _ in range(9)]})

    assert response.status_code == 400
    assert response.get_json()['error'] == 'No game in progress'


def test_post_hint_valid_response_contains_one_solution_value():
    with app_module.app.test_client() as client:
        client.get('/new?clues=35')
        puzzle = copy.deepcopy(app_module.CURRENT['puzzle'])
        solution = app_module.CURRENT['solution']

        response = client.post('/hint', json={'board': copy.deepcopy(puzzle)})

    assert response.status_code == 200
    data = response.get_json()
    assert set(data) == {'row', 'col', 'value', 'hint_count'}
    assert puzzle[data['row']][data['col']] == 0
    assert data['value'] == solution[data['row']][data['col']]
    assert data['hint_count'] == 1
    assert len(app_module.CURRENT['hinted_cells']) == 1


def test_post_hint_selects_a_different_cell_after_first_hint():
    with app_module.app.test_client() as client:
        client.get('/new?clues=35')
        board = copy.deepcopy(app_module.CURRENT['puzzle'])

        first = client.post('/hint', json={'board': board}).get_json()
        board[first['row']][first['col']] = first['value']
        second = client.post('/hint', json={'board': board}).get_json()

    assert (second['row'], second['col']) != (first['row'], first['col'])
    assert second['hint_count'] == 2
    assert len(app_module.CURRENT['hinted_cells']) == 2


def test_post_hint_skips_user_filled_and_prefilled_cells():
    with app_module.app.test_client() as client:
        client.get('/new?clues=35')
        puzzle = copy.deepcopy(app_module.CURRENT['puzzle'])
        board = copy.deepcopy(puzzle)
        first_empty = next(
            (row, col)
            for row in range(9)
            for col in range(9)
            if puzzle[row][col] == 0
        )
        board[first_empty[0]][first_empty[1]] = 1

        response = client.post('/hint', json={'board': board})

    data = response.get_json()
    assert (data['row'], data['col']) != first_empty
    assert puzzle[data['row']][data['col']] == 0


def test_post_hint_rejects_invalid_board_structure_and_values():
    with app_module.app.test_client() as client:
        client.get('/new?clues=35')

        bad_shape = client.post('/hint', json={'board': []})
        bad_value_board = [[0 for _ in range(9)] for _ in range(9)]
        bad_value_board[0][0] = 10
        bad_value = client.post('/hint', json={'board': bad_value_board})

    assert bad_shape.status_code == 400
    assert bad_value.status_code == 400


def test_hint_state_resets_after_new_game():
    with app_module.app.test_client() as client:
        client.get('/new?clues=35')
        board = copy.deepcopy(app_module.CURRENT['puzzle'])
        client.post('/hint', json={'board': board})
        assert app_module.CURRENT['hint_count'] == 1

        client.get('/new?clues=35')

    assert app_module.CURRENT['hint_count'] == 0
    assert app_module.CURRENT['hinted_cells'] == set()


def test_post_hint_with_no_eligible_cells_does_not_increment_count():
    with app_module.app.test_client() as client:
        client.get('/new?clues=35')
        solution = copy.deepcopy(app_module.CURRENT['solution'])

        response = client.post('/hint', json={'board': solution})

    assert response.status_code == 200
    data = response.get_json()
    assert data['message'] == 'No empty cells remain for a hint'
    assert data['hint_count'] == 0
    assert app_module.CURRENT['hinted_cells'] == set()


def test_post_hint_does_not_return_the_full_solution():
    with app_module.app.test_client() as client:
        client.get('/new?clues=35')
        solution = app_module.CURRENT['solution']
        response = client.post('/hint', json={'board': app_module.CURRENT['puzzle']})

    assert 'solution' not in response.get_json()
    assert response.get_json() != solution
