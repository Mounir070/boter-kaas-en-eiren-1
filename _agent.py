import random
from abc import ABC, abstractmethod
from typing import List, Tuple, Dict

from _core import opponent, is_free, is_winner, is_board_full, can_win
from _typing import Board, Symbol


class Agent(ABC):
    @abstractmethod
    def move(self, board: Board, my_symbol: Symbol) -> int:
        raise NotImplemented()

    def explore_move(self,
                     board: Board,
                     symbol: Symbol,
                     move: int) -> Board:
        new_board = [*board]
        new_board[move] = symbol
        return new_board

    def get_moves_and_boards(self,
                             board: Board,
                             symbol: Symbol) -> List[Tuple[int, Board]]:
        moves = [i for i in range(9) if is_free(board, i)]
        moves_scenarios = [(m, self.explore_move(board, symbol, m))
                           for m in moves]
        return moves_scenarios


class EvaluationAgent(Agent):
    def move(self, board: Board, my_symbol: Symbol) -> int:
        opponent_symbol = opponent[my_symbol]
        moves_scenarios = self.get_moves_and_boards(board, my_symbol)
        evaluations = [(self.evaluate(s, my_symbol, opponent_symbol), m)
                       for m, s in moves_scenarios]
        evaluations.sort(reverse=True)
        return evaluations[0][1]

    @abstractmethod
    def evaluate(self,
                 board: Board,
                 my_symbol: Symbol,
                 opponent_symbol: Symbol) -> int:
        raise NotImplemented()


class OptimalEvaluationAgent(EvaluationAgent):
    def evaluate(self, board: Board, my_symbol: Symbol, opponent_symbol: Symbol) -> int:
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


class MLAgent(Agent):
    def __init__(self,
                 epsilon: float = 0.1,  # Exploration rate
                 alpha: float = 1.0):  # Learning rate
        assert 0 <= epsilon <= 1, 'epsilon must be between 0 and 1'
        assert 0 <= alpha <= 1, 'epsilon must be between 0 and 1'
        self.learning: bool = True
        self._symbol: str = None
        self._epsilon: float = epsilon
        self._alpha: float = alpha
        self._memory: Dict[str, float] = {}

    def evaluate(self, board: Board) -> float:
        if is_winner(board, self.symbol):
            reward = 1
        elif is_winner(board, opponent[self.symbol]):
            reward = -1
        else:
            reward = 0
        return reward

    def move(self, board: Board, my_symbol: Symbol) -> int:
        self._symbol = self._symbol or my_symbol
        move_ = self._minmax(board, my_symbol)
        if self.learning:
            # Imagine the board after our chosen move.
            next_board = self.explore_move(board, my_symbol, move_)

            next_mem_value = 0
            if (not is_winner(next_board, my_symbol)
                    and not is_winner(next_board, opponent[my_symbol])
                    and not is_board_full(next_board)):
                # If there would still be a move.
                next_move = self._minmax(next_board, opponent[my_symbol])
                next_next_board = self.explore_move(next_board,
                                                    opponent[my_symbol],
                                                    next_move)
                next_mem_value = self._value_from_memory(next_next_board)
            evaluation = self.evaluate(next_board)
            mem_value = self._value_from_memory(next_board)
            new_value = mem_value + self._alpha * (evaluation + next_mem_value)
            self._store_value(next_board, new_value)
        return move_

    @property
    def symbol(self):
        return self._symbol

    def _value_from_memory(self, board: Board) -> float:
        return self._memory.get(self._hash_board(board), 0)

    def _hash_board(self, board: Board) -> str:
        return ''.join(board)

    def _store_value(self, board: Board, value: float):
        self._memory[self._hash_board(board)] = value

    def _minmax(self, board: Board, symbol: Symbol) -> int:
        moves_scenarios = self.get_moves_and_boards(board, symbol)
        value_per_move = {m: self._value_from_memory(s)
                          for m, s in moves_scenarios}
        if self.learning and random.random() < self._epsilon:
            # Pick a random move (exploration).
            options = list(value_per_move.keys())
        else:
            # Pick an optimal move (exploitation).
            func = max if symbol is self.symbol else min
            best_or_worst_value = func(value_per_move.values())
            options = [m for m in value_per_move
                       if value_per_move[m] == best_or_worst_value]
        return random.choice(options)


class RandomAgent(Agent):
    def move(self, board: Board, my_symbol: Symbol) -> int:
        return random.choice(self.get_moves_and_boards(board, my_symbol))[0]
