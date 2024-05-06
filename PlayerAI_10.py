import random
from typing import Tuple

from Grid_10 import Grid

# This is akin to BaseAI in HW2, each member will make their own class with some method of getting move


class MoveStrategy:

    def __init__(self):
        self.prev_move = None

    def get_prev_move_result(self, board: Grid):
        if self.prev_move == None:
            return "Have not made a move yet"
        x, y = self.prev_move
        if board.map[y][x] == Grid.SPACE["empty"]:
            return f"x:{x} y:{y} has not been fired on"
        elif board.map[y][x] == Grid.SPACE["miss"]:
            return "miss"
        elif board.map[y][x] == Grid.SPACE['hit']:
            return "hit"
        else:
            return "sunk"

    def get_move(self, move: str) -> Tuple[int, int]:
        """
        make sure to set self.prev_move to whatever move you determine
        """
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
        choice = random.choice(choices)
        # save prev move, just assuming after this function we call make_move
        self.prev_move = choice
        return (0, 0) if len(choices) == 0 else choice
