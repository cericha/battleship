import random
from typing import Tuple

from Grid_10 import Grid

# This is akin to BaseAI in HW2, each member will make their own class with some method of getting move


class PlayerAI:
    def parse_move(self, move: str) -> Tuple[int, int]:
        return tuple(map(int, str(move).split(" ")))

    def getMove(self, board: Grid) -> Tuple[int, int]:
        move = input("Enter next move: ")
        return self.parse_move(move)
