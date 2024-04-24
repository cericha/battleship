import random
from typing import Tuple

from Grid_10 import Grid

# This is akin to BaseAI in HW2, each member will make their own class with some method of getting move


class PlayerAI:
    def getMove(self, board: Grid) -> Tuple[int, int]:
        choices = board.getEmptySpaces()
        return (0, 0) if len(choices) == 0 else random.choice(choices)
