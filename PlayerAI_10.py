import random
from typing import Tuple

from Grid_10 import Grid

# This is akin to BaseAI in HW2, each member will make their own class with some method of getting move


class PlayerAI:
    def __init__(self, strategy=None):
        self.strategy = strategy

    def parse_move(self, move: str) -> Tuple[int, int]:
        return tuple(map(int, str(move).split(" ")))

    def getMove(self, board: Grid) -> Tuple[int, int]:
        # TODO: Maybe make each strategy a class?
        if self.strategy is None or self.strategy == "baseline":
            return self.getMoveBaseline(board)
        elif self.strategy == "human":
            return self.getMoveHuman(board)
        else:
            print(f"Solution strategy for {self.strategy} does not exit. Exiting")
            exit(1)

    def getMoveHuman(self, board: Grid):
        move = input("Enter next move: ")
        return self.parse_move(move)

    def getMoveBaseline(self, board: Grid):
        choices = board.getEmptySpaces()
        return (0, 0) if len(choices) == 0 else random.choice(choices)
