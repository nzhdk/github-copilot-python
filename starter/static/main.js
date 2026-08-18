// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const SCOREBOARD_STORAGE_KEY = 'sudokuTopScores';
const THEME_STORAGE_KEY = 'sudokuTheme';
const THEMES = ['light', 'dark'];
const MAX_SCORE_COUNT = 10;
const MAX_NAME_LENGTH = 30;
let puzzle = [];
let selectedDifficulty = 'medium';
let hintCount = 0;
let timerStartedAt = null;
let elapsedBeforeStartMs = 0;
let elapsedTimeMs = 0;
let timerIntervalId = null;
let completedTimeMs = null;
let scoreSubmitted = false;

function getStoredTheme() {
  try {
    const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
    return THEMES.includes(storedTheme) ? storedTheme : 'light';
  } catch (error) {
    return 'light';
  }
}

function applyTheme(theme) {
  const selectedTheme = THEMES.includes(theme) ? theme : 'light';
  document.documentElement.dataset.theme = selectedTheme;

  const themeToggle = document.getElementById('theme-toggle');
  if (themeToggle) {
    const isDark = selectedTheme === 'dark';
    themeToggle.setAttribute('aria-pressed', String(isDark));
    themeToggle.setAttribute('aria-label', `Switch to ${isDark ? 'light' : 'dark'} mode`);
    themeToggle.textContent = isDark ? 'Light mode' : 'Dark mode';
  }
}

function saveTheme(theme) {
  try {
    window.localStorage.setItem(THEME_STORAGE_KEY, theme);
  } catch (error) {
    // Theme changes still apply when browser storage is unavailable.
  }
}

function toggleTheme() {
  const nextTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(nextTheme);
  saveTheme(nextTheme);
}

function setMessageTone(message, tone) {
  message.classList.remove('status-error', 'status-success');
  if (tone) message.classList.add(`status-${tone}`);
}

function formatElapsedTime(elapsedMs) {
  const totalSeconds = Math.floor(Math.max(0, elapsedMs) / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

function readScores() {
  try {
    const storedScores = window.localStorage.getItem(SCOREBOARD_STORAGE_KEY);
    if (!storedScores) return [];

    const scores = JSON.parse(storedScores);
    if (!Array.isArray(scores)) return [];

    return scores
      .filter((score) => (
        score &&
        typeof score.name === 'string' &&
        score.name.trim().length > 0 &&
        Number.isFinite(score.timeMs) &&
        score.timeMs >= 0 &&
        typeof score.difficulty === 'string' &&
        Number.isInteger(score.hints) &&
        score.hints >= 0
      ))
      .map((score) => ({
        name: score.name.trim().slice(0, MAX_NAME_LENGTH),
        timeMs: score.timeMs,
        difficulty: score.difficulty,
        hints: score.hints
      }))
      .sort((first, second) => first.timeMs - second.timeMs)
      .slice(0, MAX_SCORE_COUNT);
  } catch (error) {
    return [];
  }
}

function writeScores(scores) {
  try {
    window.localStorage.setItem(SCOREBOARD_STORAGE_KEY, JSON.stringify(scores));
    return true;
  } catch (error) {
    return false;
  }
}

function addScore(score) {
  const scores = readScores();
  scores.push(score);
  scores.sort((first, second) => first.timeMs - second.timeMs);
  return writeScores(scores.slice(0, MAX_SCORE_COUNT));
}

function renderScoreboard() {
  const scoreboardBody = document.getElementById('scoreboard-body');
  if (!scoreboardBody) return;

  scoreboardBody.replaceChildren();
  const scores = readScores();
  if (scores.length === 0) {
    const emptyRow = document.createElement('tr');
    const emptyCell = document.createElement('td');
    emptyCell.colSpan = 5;
    emptyCell.textContent = 'No scores yet. Complete a puzzle to be the first entry.';
    emptyRow.appendChild(emptyCell);
    scoreboardBody.appendChild(emptyRow);
    return;
  }

  scores.forEach((score, index) => {
    const row = document.createElement('tr');
    const rankCell = document.createElement('td');
    const nameCell = document.createElement('td');
    const timeCell = document.createElement('td');
    const difficultyCell = document.createElement('td');
    const hintsCell = document.createElement('td');

    rankCell.textContent = String(index + 1);
    nameCell.textContent = score.name;
    timeCell.textContent = formatElapsedTime(score.timeMs);
    difficultyCell.textContent = score.difficulty;
    hintsCell.textContent = String(score.hints);

    row.append(rankCell, nameCell, timeCell, difficultyCell, hintsCell);
    scoreboardBody.appendChild(row);
  });
}

function setScoreFormVisibility(isVisible) {
  const scoreForm = document.getElementById('score-form');
  const scoreFormMessage = document.getElementById('score-form-message');
  if (!scoreForm) return;

  scoreForm.hidden = !isVisible;
  if (scoreFormMessage) scoreFormMessage.textContent = '';
  if (isVisible) document.getElementById('player-name').focus();
}

function submitScore(event) {
  event.preventDefault();
  if (completedTimeMs === null || scoreSubmitted) return;

  const nameInput = document.getElementById('player-name');
  const scoreFormMessage = document.getElementById('score-form-message');
  const name = nameInput.value.trim().slice(0, MAX_NAME_LENGTH);
  nameInput.value = name;
  if (!name) {
    scoreFormMessage.textContent = 'Please enter a name.';
    nameInput.focus();
    return;
  }

  const scoreSaved = addScore({
    name,
    timeMs: completedTimeMs,
    difficulty: selectedDifficulty,
    hints: hintCount
  });
  if (!scoreSaved) {
    scoreFormMessage.textContent = 'Unable to save the score in this browser.';
    return;
  }

  scoreSubmitted = true;
  renderScoreboard();
  setScoreFormVisibility(false);
}

function updateTimerDisplay() {
  if (timerStartedAt !== null) {
    elapsedTimeMs = elapsedBeforeStartMs + performance.now() - timerStartedAt;
  }

  const timer = document.getElementById('timer');
  if (timer) {
    timer.innerText = formatElapsedTime(elapsedTimeMs);
    timer.dateTime = `PT${Math.floor(elapsedTimeMs / 1000)}S`;
  }
}

function startTimer() {
  if (timerIntervalId !== null) {
    clearInterval(timerIntervalId);
    timerIntervalId = null;
  }
  if (timerStartedAt === null) {
    timerStartedAt = performance.now();
  }
  updateTimerDisplay();
  timerIntervalId = setInterval(updateTimerDisplay, 250);
}

function stopTimer() {
  if (timerStartedAt !== null) {
    elapsedTimeMs = elapsedBeforeStartMs + performance.now() - timerStartedAt;
    elapsedBeforeStartMs = elapsedTimeMs;
    timerStartedAt = null;
  }

  if (timerIntervalId !== null) {
    clearInterval(timerIntervalId);
    timerIntervalId = null;
  }
  updateTimerDisplay();
}

function resetTimer() {
  if (timerIntervalId !== null) {
    clearInterval(timerIntervalId);
    timerIntervalId = null;
  }
  timerStartedAt = null;
  elapsedBeforeStartMs = 0;
  elapsedTimeMs = 0;
  updateTimerDisplay();
}

function getConflicts(row, col, value) {
  /**
   * Returns array of [row, col] for all editable cells with the same value
   * in the same row, column, or 3x3 box.
   * Empty cells and prefilled cells are never returned.
   */
  const conflicts = [];
  
  if (!value) return conflicts; // Empty cells have no conflicts
  
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  
  // Check row
  for (let j = 0; j < SIZE; j++) {
    if (j !== col) {
      const idx = row * SIZE + j;
      const inp = inputs[idx];
      if (inp.value === value && !inp.disabled) {
        conflicts.push([row, j]);
      }
    }
  }
  
  // Check column
  for (let i = 0; i < SIZE; i++) {
    if (i !== row) {
      const idx = i * SIZE + col;
      const inp = inputs[idx];
      if (inp.value === value && !inp.disabled) {
        conflicts.push([i, col]);
      }
    }
  }
  
  // Check 3x3 box
  const boxRow = row - row % 3;
  const boxCol = col - col % 3;
  for (let i = boxRow; i < boxRow + 3; i++) {
    for (let j = boxCol; j < boxCol + 3; j++) {
      if ((i !== row || j !== col) && i >= 0 && i < SIZE && j >= 0 && j < SIZE) {
        const idx = i * SIZE + j;
        const inp = inputs[idx];
        if (inp.value === value && !inp.disabled) {
          conflicts.push([i, j]);
        }
      }
    }
  }
  
  return conflicts;
}

function updateConflictMarkings() {
  /**
   * Scans all editable cells and marks those involved in conflicts.
   * A conflict is a duplicate value in the same row, column, or 3x3 box.
   * Prefilled cells are never marked as conflicts.
   * All conflicting editable cells get the 'conflict' class.
   */
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  
  // First pass: clear all conflict markings
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (!inp.disabled) {
      inp.classList.remove('conflict');
    }
  }
  
  // Second pass: mark all conflicts
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const inp = inputs[idx];
      if (inp.disabled) continue; // Skip prefilled cells
      
      const value = inp.value;
      if (!value) continue; // Skip empty cells
      
      const conflicts = getConflicts(i, j, value);
      if (conflicts.length > 0) {
        // Mark the current cell
        inp.classList.add('conflict');
        // Mark all conflicting cells
        for (const [conflictRow, conflictCol] of conflicts) {
          const conflictIdx = conflictRow * SIZE + conflictCol;
          inputs[conflictIdx].classList.add('conflict');
        }
      }
    }
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      if ((Math.floor(i / 3) + Math.floor(j / 3)) % 2 === 1) {
        input.classList.add('region-alt');
      }
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        updateConflictMarkings();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
  updateConflictMarkings();
}

function collectPlayerBoard() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const val = inputs[i * SIZE + j].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

function updateHintCount(count) {
  hintCount = count;
  document.getElementById('hint-count').innerText = `Hints: ${hintCount}`;
}

async function newGame() {
  const res = await fetch(`/new?difficulty=${selectedDifficulty}`);
  const data = await res.json();
  if (!res.ok || data.error) {
    const message = document.getElementById('message');
    setMessageTone(message, 'error');
    message.innerText = data.error || 'Unable to start a new game.';
    return;
  }
  renderPuzzle(data.puzzle);
  updateHintCount(0);
  const message = document.getElementById('message');
  setMessageTone(message, null);
  message.innerText = '';
  completedTimeMs = null;
  scoreSubmitted = false;
  setScoreFormVisibility(false);
  resetTimer();
  startTimer();
}

async function requestHint() {
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board: collectPlayerBoard()})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    setMessageTone(msg, 'error');
    msg.innerText = data.error;
    return;
  }
  if (data.message) {
    setMessageTone(msg, 'error');
    msg.innerText = data.message;
    return;
  }

  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const input = inputs[data.row * SIZE + data.col];
  if (input.disabled || input.value) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'That cell is already filled.';
    return;
  }
  input.value = data.value;
  input.disabled = true;
  input.classList.add('hinted');
  updateHintCount(data.hint_count);
  updateConflictMarkings();
  setMessageTone(msg, 'success');
  msg.innerText = 'Hint added.';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = collectPlayerBoard();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    setMessageTone(msg, 'error');
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.classList.remove('incorrect');
    if (incorrect.has(idx)) {
      inp.classList.add('incorrect');
    }
  }
  if (incorrect.size === 0) {
    if (completedTimeMs === null) {
      stopTimer();
      completedTimeMs = elapsedTimeMs;
      setScoreFormVisibility(true);
    }
    setMessageTone(msg, 'success');
    msg.innerText = 'Congratulations! You solved it!';
  } else {
    setMessageTone(msg, 'error');
    msg.innerText = 'Some cells are incorrect.';
  }
}

// Handle difficulty selection
function setupDifficultySelector() {
  const difficultyBtns = document.querySelectorAll('.difficulty-btn');
  difficultyBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      // Update selected difficulty
      selectedDifficulty = btn.dataset.difficulty;
      
      // Update visual state
      difficultyBtns.forEach(b => {
        b.classList.remove('active');
        b.setAttribute('aria-pressed', 'false');
      });
      btn.classList.add('active');
      btn.setAttribute('aria-pressed', 'true');
    });
  });
}

// Wire buttons
window.addEventListener('load', () => {
  applyTheme(getStoredTheme());
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  setupDifficultySelector();
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint').addEventListener('click', requestHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('score-form').addEventListener('submit', submitScore);
  renderScoreboard();
  // initialize
  newGame();
});