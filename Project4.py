from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

ROWS = 6
COLUMNS = 7

EMPTY = 0
PLAYER1 = 1
PLAYER2 = 2

@dataclass
class GameState:
    current_player: int = PLAYER1
    search_depth: int = 4
    heuristic: str = "Score"

@dataclass
class Analysis:
    recommended_move: Optional[int]
    updated_board: List[List[int]]
    winning_moves: List[int]
    search: Dict[str, Any]

def create_analysis() -> Analysis:
    analysis = Analysis()
    analysis.recommended_move = None
    analysis.updated_board = [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]
    analysis.winning_moves = []
    analysis.search = {}
    return analysis

def create_board() -> list[list[int]]:
    return [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]

def column(board: list[list[int]], column: int) -> list[int]:
    return [row[column] for row in board]

def valid_column(board: list[list[int]], column: int) -> bool:
    return board[0][column] == EMPTY

def next_row(board: list[list[int]], column: int) -> Optional[int]:
    for row in range(ROWS - 1, -1, -1):
        if board[row][column] == EMPTY:
            return row
    return None

def checker(board: list[list[int]], row: int, column: int, player: int) -> None:
    if board[row][column] == EMPTY:
        board[row][column] = player
        return True
    return False

def copy_board(board: list[list[int]]) -> list[list[int]]:
    return [row[:] for row in board]

def position(board: list[list[int]], state: GameState) -> Analysis:
    analysis = create_analysis()
    board = copy_board(board)

    for column in range(COLUMNS):
        if valid_column(board, column):
            row = next_row(board, column)
            if row is not None:
                checker(board, row, column, state.current_player)
                analysis.recommended_move = column
                analysis.updated_board = board
                break

            analysis.search = {
                    "depth": state.search_depth,
                    "heuristic": state.heuristic,
                    "node": 1
                }
            return analysis

def analysis_save(filename: str, analysis: Analysis) -> None:
    data = {
        "recommended_move": analysis.recommended_move,
        "updated_board": analysis.updated_board,
        "winning_moves": analysis.winning_moves,
        "search": analysis.search
    }
    with open(filename, "w") as f:
        json.dump(analysis.search, f)

def load_board(filename: str) -> tuple[list[list[int]], list[Analysis]]:
    with open(filename, "r") as f:
        data = json.load(f)

        board = data["board"]

        state = GameState()
        state.current_player = data.get["current_player", PLAYER1]
        state.search_depth = data.get["search_depth", 4]
        state.heuristic = data.get["heuristic", "Score"]
        return board, state
