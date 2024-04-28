import random
from typing import Tuple

from Grid_10 import Grid

# This is akin to BaseAI in HW2, each member will make their own class with some method of getting move


class MoveStrategy:

    def __init__(self, strategy=None):
        self.strategy = strategy

    def get_move(self, move: str) -> Tuple[int, int]:
        pass


class HumanPlayer(MoveStrategy):

    def parse_move(self, move: str) -> Tuple[int, int]:
        return tuple(map(int, str(move).split(" ")))

    def get_move(self, board: Grid):
        move = input("Enter next move: ")
        return self.parse_move(move)


class BaselineAI(MoveStrategy):

    def get_move(self, board: Grid):
        choices = board.getEmptySpaces()
        return (0, 0) if len(choices) == 0 else random.choice(choices)
