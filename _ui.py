import textwrap

from _typing import Board, Symbol, UI


def draw_board(board: Board):
    board_str = """
     {} | {} | {}
    ---+---+---
     {} | {} | {}
    ---+---+---
     {} | {} | {} 
    """.format(*[place for place in board])
    print(textwrap.dedent(board_str))


def draw_start():
    print('Boter Kaas en Eieren')
    print('====================')
    print()


def draw_turn(round_nr: int, turn: Symbol):
    print()
    print(f'Ronde {round_nr}')
    print(f'Beurt: {turn}')


def draw_game_over(board: Board, winner: Symbol):
    print()
    print('Het spel is voorbij')
    draw_board(board)
    if winner:
        print(f'{winner} heeft gewonnen!')
    else:
        print('Gelijk spel!')
    print()


def get_player_move(board: Board, player_symbol: Symbol) -> int:
    msg = textwrap.dedent(f"""
        0 1 2
        3 4 5
        6 7 8    
        Plaats een {player_symbol} op een vrij vlak, kies een getal:
        """).strip()
    print(msg)
    move = input()
    while move not in [str(x) for x in range(9)]:
        print('Kies een getal 0 t/m 8')
        move = input()
    return int(move)


STD_UI = UI(draw_board, draw_start, draw_turn, draw_game_over, get_player_move)
HEADLESS = UI()
