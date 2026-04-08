from __future__ import annotations

import json
import math
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

ROWS = 6
COLUMNS = 7

EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2


#Functions for reading the game state
@dataclass
class GameState:
    current_player: int = PLAYER1
    search_depth: int = 4
    heuristic: str = "Score"

@dataclass
class Analysis:
    recommended_move: Optional[int] = None
    updated_board: List[List[int]] = field(default_factory=list)
    winning_moves: List[int] = field(default_factory=list)
    search: Dict[str, Any] = field(default_factory=dict)

#Functions for interacting with the board
def create_board() -> list[list[int]]:
    return [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]

def valid_column(board, column):
    return board[0][column] == EMPTY

def next_row(board, column):
    for row in range(ROWS - 1, -1, -1):
        if board[row][column] == EMPTY:
            return row
    return None

def copy_board(board):
    return [row[:] for row in board]

def drop_piece(board, row, col, player):
    board[row][col] = player

def get_valid_moves(board):
    return [c for c in range(COLUMNS) if valid_column(board, c)]

#Checks for a winner, returns false and continues the game if no winner is found
def check_winner(board, player):
    # Horizontal
    for r in range(ROWS):
        for c in range(COLUMNS - 3):
            if all(board[r][c+i] == player for i in range(4)):
                return True

    # Vertical
    for r in range(ROWS - 3):
        for c in range(COLUMNS):
            if all(board[r+i][c] == player for i in range(4)):
                return True

    # Diagonal L Down to R Up
    for r in range(ROWS - 3):
        for c in range(COLUMNS - 3):
            if all(board[r+i][c+i] == player for i in range(4)):
                return True

    # Diagonal L Up to R Down
    for r in range(3, ROWS):
        for c in range(COLUMNS - 3):
            if all(board[r-i][c+i] == player for i in range(4)):
                return True

    return False


def evaluate(board):
    if check_winner(board, PLAYER1):
        return 100
    if check_winner(board, PLAYER2):
        return -100

    score = 0

    # Score center column slightly
    center_col = [board[r][COLUMNS // 2] for r in range(ROWS)]
    score += center_col.count(PLAYER1) * 3

    # Check all positions for potential 2 or 3 in a row
    for r in range(ROWS):
        for c in range(COLUMNS - 3):
            window = board[r][c:c+4]
            score += score_window(window, PLAYER1)
            score -= score_window(window, PLAYER2)  # subtract opponent potential

    for c in range(COLUMNS):
        for r in range(ROWS - 3):
            window = [board[r+i][c] for i in range(4)]
            score += score_window(window, PLAYER1)
            score -= score_window(window, PLAYER2)

    for r in range(ROWS - 3):
        for c in range(COLUMNS - 3):
            window = [board[r+i][c+i] for i in range(4)]
            score += score_window(window, PLAYER1)
            score -= score_window(window, PLAYER2)

    for r in range(3, ROWS):
        for c in range(COLUMNS - 3):
            window = [board[r-i][c+i] for i in range(4)]
            score += score_window(window, PLAYER1)
            score -= score_window(window, PLAYER2)

    return score

def score_window(window, player):
    """Score a 4-cell window for the given player"""
    score = 0
    opp = PLAYER1 if player == PLAYER2 else PLAYER2
    #Winning state
    if window.count(player) == 4:
        score += 100
    elif window.count(player) == 3 and window.count(EMPTY) == 1:
        #3 in a row
        score += 10
    elif window.count(player) == 2 and window.count(EMPTY) == 2:
        #2 in a row
        score += 5
    if window.count(opp) == 3 and window.count(EMPTY) == 1:
        score -= 8  # block opponent
    return score

#MiniMax tree function
def minimax(board, depth, alpha, beta, maximizing):
    valid_moves = get_valid_moves(board)

    if depth == 0 or not valid_moves or check_winner(board, PLAYER1) or check_winner(board, PLAYER2):
        return evaluate(board), None

    if maximizing:
        max_eval = -math.inf
        best_move = valid_moves[0]

        for move in valid_moves:
            row = next_row(board, move)
            if row is None:
                continue
            temp = copy_board(board)
            drop_piece(temp, row, move, PLAYER1)

            eval_score, _ = minimax(temp, depth - 1, alpha, beta, False)

            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move

            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break

        return max_eval, best_move

    else:
        min_eval = math.inf
        best_move = valid_moves[0]

        for move in valid_moves:
            row = next_row(board, move)
            if row is None:
                continue
            temp = copy_board(board)
            drop_piece(temp, row, move, PLAYER2)

            eval_score, _ = minimax(temp, depth - 1, alpha, beta, True)

            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move

            beta = min(beta, eval_score)
            if beta <= alpha:
                break

        return min_eval, best_move

#Main function
def position(board: list[list[int]], state: GameState) -> Analysis:
    analysis = Analysis()
    board = copy_board(board)
    analysis.updated_board = copy_board(board)

    for col in get_valid_moves(board):
        row = next_row(board, col)
        if row is not None:
            temp = copy_board(board)
            drop_piece(temp, row, col, state.current_player)
            if check_winner(temp, state.current_player):
                analysis.winning_moves.append(col)

    maximizing = (state.current_player == PLAYER1)

    score, move = minimax(
        board,
        state.search_depth,
        -math.inf,
        math.inf,
        maximizing
    )

    analysis.recommended_move = move

    if move is not None:
        row = next_row(board, move)
        if row is not None:
            drop_piece(board, row, move, state.current_player)
            analysis.updated_board = board

    analysis.search = {
        "depth": state.search_depth,
        "score": score
    }

    return analysis


#Reads JSON file
def analysis_save(filename: str, analysis: Analysis) -> None:
    data = {
        "recommended_move": analysis.recommended_move,
        "updated_board": analysis.updated_board,
        "winning_moves": analysis.winning_moves,
        "search": analysis.search
    }
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)

def load_board(filename: str):
    with open(filename, "r") as f:
        data = json.load(f)

    board = data["board"]

    state = GameState(
        current_player=data.get("current_player", PLAYER1),
        search_depth=data.get("search_depth", 4),
        heuristic=data.get("heuristic", "Score")
    )

    return board, state

if __name__ == "__main__":

    board, state = load_board("input.json")
    analysis = position(board, state)
    analysis_save("data.json", analysis)
    print("Your recommended move is: Column " + str(analysis.recommended_move))

   