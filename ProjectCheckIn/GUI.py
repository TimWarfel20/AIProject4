import tkinter as tk
from tkinter import messagebox

import board
import state

from file import (
    PLAYER1,
    PLAYER2,
    ROWS,
    COLUMNS,
    EMPTY,
    GameState,
    create_board,
    checker,
    position,
    analysis_save, next_row
)

class connectFourInterface:
    def __init__(self):
        board = create_board()
    state = GameState()
    previous_result = None
    board_slot = []

    root = tk.Tk()
    def board_display():
            for row in range(ROWS):
                for col in range(COLUMNS):
                    value = board[row][col]

                    if value == EMPTY:
                        color = "black"
                    elif value == PLAYER1:
                        color = "red"
                    else:
                        color = "yellow"

                    labels_board[row][col].config(bg=color)
                    if state.current_player == PLAYER1:
                        label_current_player.config(text="current player: Red")
                    else:
                        label_current_player.config(text="current player: yellow")

def drop_checker(column):
    row = next_row(board, column)

    if row is None:
        messagebox.showerror("Error", "You can't go there!")
        return

    checker(board, row, column, state.current_player)
    board_display()

def analyze():
    global previous_result
    previous_result = position(board, state)
    label_bestmove.config(text="Best Move")

def player_switch():
    if state.current_player == PLAYER1:
        state.current_player = PLAYER2
    else:
        state.current_player = PLAYER1
        board_display()

def clear_board():
    global board, previous_result
    board = create_board()
    previous_result = None
    label_bestmove.config(text="Recommended Move: None")
    board_display()

def save_board():
    global previous_result
    if previous_result is None:
        previous_result = position(board, state)
analysis_save("output.json" previous_result)
messagebox.showinfo("saved")
