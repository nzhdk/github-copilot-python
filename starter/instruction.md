# Copilot Instructions — Sudoku Refactoring Project

## Project Goal

Refactor the legacy Flask Sudoku application into a modern, modular,
maintainable Sudoku game while preserving existing functionality.

## Technology

- Python
- Flask
- HTML
- CSS
- JavaScript
- Browser localStorage
- pytest

## Code Quality

- Write clear, readable, maintainable Python.
- Use small, reusable functions.
- Separate Sudoku/game logic from Flask routes and presentation.
- Use meaningful names.
- Avoid unnecessary duplication.
- Prefer simple solutions over unnecessary complexity.
- Preserve existing functionality unless a requirement explicitly changes it.
- Include appropriate error handling.
- Avoid unnecessary dependencies.

## Sudoku Logic

The application must:

- Generate valid 9x9 Sudoku puzzles.
- Ensure every generated puzzle has exactly one unique solution.
- Support Easy, Medium, and Hard difficulty levels.
- Keep prefilled cells locked.
- Detect invalid/conflicting entries.
- Detect successful puzzle completion.

When modifying Sudoku generation, prioritize correctness and testability.

## Game Features

The final application must support:

- Difficulty selection.
- Timer.
- Hint button.
- Check button.
- Immediate visual feedback for invalid entries.
- Completion message.
- Top 10 fastest scores.
- Player name, completion time, difficulty, and number of hints.
- Persistent scoreboard using browser localStorage.
- Light and dark modes.

## UI Requirements

- Responsive on desktop and mobile.
- Clear and readable controls.
- Alternating styling for the 3x3 Sudoku regions.
- Good contrast in light and dark modes.
- Avoid layout shifts.
- Keep controls accessible and understandable.

## Testing

- Do not remove or weaken existing tests.
- Run the test suite after every significant change.
- Add tests for important new functionality.
- Preserve a working baseline.
- Do not modify application behavior merely to make an incorrect test pass.

## Copilot Workflow

For major changes:

1. Inspect the existing implementation first.
2. Explain the proposed approach before making changes.
3. Identify important edge cases.
4. Make focused changes rather than rewriting unrelated code.
5. Run relevant tests.
6. Explain unfamiliar code when requested.
7. Evaluate generated code instead of blindly accepting it.
8. Reject or modify suggestions that are unnecessarily complex,
   incorrect, or inconsistent with the project requirements.

## Important Constraint

Do not introduce future features while working on an isolated milestone.
Implement and verify one major requirement at a time.