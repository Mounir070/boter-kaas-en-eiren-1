from functools import partial
from typing import List, Optional

from _typing import (
    Board,
    Symbol,
    Player,
    PLAYER_X,
    PLAYER_O,
    PLAYER_EMPTY,
    UI,
    StateObserver
)
from _ui import STD_UI

opponent = {
    PLAYER_X: PLAYER_O,
    PLAYER_O: PLAYER_X
}


def possible_scenarios(
        board: Board,
        opponent_symbol: Symbol) -> List[Board]:
    opponent_moves = [i for i in range(9) if is_free(board, i)]
    return [_make_move(board, opponent_symbol, m) for m in opponent_moves]


def can_win(board: Board, symbol: Symbol) -> bool:
    winning_scenarios = [s for s in possible_scenarios(board, symbol)
                         if is_winner(s, symbol)]
    return bool(winning_scenarios)


def default_evaluate_scenario(
        board: Board,
        my_symbol: Symbol,
        opponent_symbol: Symbol) -> int:
    if is_winner(board, my_symbol):
        return 1000

    if can_win(board, opponent_symbol):
        return 0

    if can_win(board, my_symbol):
        return 500

    result = 0
    result += 4 * (board[4] == my_symbol)
    result += 2 * (board[0] == my_symbol)
    result += 2 * (board[2] == my_symbol)
    result += 2 * (board[6] == my_symbol)
    result += 2 * (board[8] == my_symbol)
    result += 1 * (board[1] == my_symbol)
    result += 1 * (board[3] == my_symbol)
    result += 1 * (board[5] == my_symbol)
    result += 1 * (board[7] == my_symbol)

    return result


def is_winner(board: Board, symbol: Symbol) -> bool:
    sequences = [
        board[0:3],    # 0 1 2
        board[3:6],    # 3 4 5
        board[6:],     # 6 7 8
        board[0:9:3],  # 0 3 6
        board[1:9:3],  # 1 4 7
        board[2:9:3],  # 2 5 8
        board[0:9:4],  # 0 4 8
        board[2:7:2]   # 2 4 6
    ]
    return [symbol, symbol, symbol] in sequences


def is_free(board: Board, move: int) -> bool:
    return board[move] == PLAYER_EMPTY


def is_board_full(board: Board) -> bool:
    any_space_left = bool([i for i in range(9) if is_free(board, i)])
    return not any_space_left


def _make_move(board: Board, symbol: Symbol, move: int) -> Board:
    new_board = _get_board_copy(board)
    new_board[move] = symbol
    return new_board


def _launch(player1: Player,
            player2: Player,
            state_observer: Optional[StateObserver],
            ui: UI) -> Optional[Symbol]:
    ui.draw_start()

    winner = None
    round_nr = 1
    the_board = [PLAYER_EMPTY] * 9

    players = [player1, player2]

    player_per_symbol = {symbol: players[i] for i, symbol in
                         enumerate(opponent.keys())}

    turn = list(player_per_symbol.keys())[0]
    game_is_playing = True
    while game_is_playing:
        ui.draw_turn(round_nr, turn)
        ui.draw_board(the_board)
        if state_observer:
            state_observer(the_board, turn)
        player_func = player_per_symbol[turn]
        move = player_func(the_board, turn)
        the_board = _make_move(the_board, turn, move)
        if is_winner(the_board, turn):
            ui.draw_game_over(the_board, turn)
            game_is_playing = False
            winner = turn
        elif is_board_full(the_board):
            ui.draw_game_over(the_board, None)
            game_is_playing = False
        else:
            turn = opponent[turn]
        round_nr += 1
    return winner


def _get_board_copy(board: Board) -> Board:
    return [i for i in board]


def _get_player_move(board: Board, player_symbol: Symbol, ui: UI) -> int:
    move = PLAYER_EMPTY
    while not isinstance(move, int) or not is_free(board, int(move)):
        move = ui.get_player_move(board, player_symbol)
    return int(move)


def _get_computer_move(
        board: Board,
        my_symbol: Symbol,
        evaluation_func: Player) -> int:
    opponent_symbol = opponent[my_symbol]
    moves = [i for i in range(9) if is_free(board, i)]
    moves_scenarios = [(m, _make_move(board, my_symbol, m))
                       for m in moves]
    evaluations = [(evaluation_func(s, my_symbol, opponent_symbol), m)
                   for m, s in moves_scenarios]
    evaluations.sort(reverse=True)
    return evaluations[0][1]


def start(player_x: Optional['Agent'] = None,
          player_o: Optional['Agent'] = None,
          state_observer: StateObserver = None,
          ui: UI = STD_UI) -> Optional[Symbol]:
    p1 = getattr(player_x, 'move', partial(_get_player_move, ui=ui))
    p2 = getattr(player_o, 'move', partial(_get_player_move, ui=ui))
    winner = _launch(p1, p2, state_observer, ui)
    return winner
