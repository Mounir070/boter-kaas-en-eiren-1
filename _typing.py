import random
from dataclasses import dataclass
from typing import List, Callable


# Constants.
PLAYER_X = 'X'
PLAYER_O = 'O'
PLAYER_EMPTY = ' '

# Core types.
Board = List[str]
Symbol = str
Player = Callable[[Board, Symbol, Symbol], int]
StateObserver = Callable[[Board, Symbol], None]

# User Interface types.
UIBoard = Callable[[Board], None]
UIStart = Callable[[], None]
UITurn = Callable[[int, Symbol], None]
UIGameOver = Callable[[Board, Symbol], None]
UIGetPlayerMove = Callable[[Board, Symbol], int]


def _empty_func(*_, **__): pass


@dataclass
class UI:
    draw_board: UIBoard = _empty_func
    draw_start: UIStart = _empty_func
    draw_turn: UITurn = _empty_func
    draw_game_over: UIGameOver = _empty_func
    get_player_move: UIGetPlayerMove = lambda *_, **__: random.randint(0, 8)
