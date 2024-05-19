from copy import deepcopy
from typing import Tuple


class Grid:
    """
    Remember, when accessing the arary, it is of form grid.map[y][x], NOT grid.map[x][y]
    """

    SPACE = {"empty": 0, "miss": "X", "hit": 1}

    def __init__(self, rows: int = 10, cols: int = 10) -> None:
        self.rows = rows
        self.cols = cols
        self.map = [[self.SPACE["empty"] for x in range(cols)] for y in range(rows)]

    def getEmptySpaces(self) -> Tuple[int, int]:
        empty_spaces = []
        for y in range(self.rows):
            for x in range(self.cols):
                if self.map[y][x] == self.SPACE["empty"]:
                    empty_spaces.append((x, y))
        return empty_spaces

    def clone(self) -> "Grid":
        gridCopy = Grid(self.rows, self.cols)
        gridCopy.map = deepcopy(self.map)

        return gridCopy

    def get_result(self, player):
        # Implement logic to determine the result of the game from this player's perspective
        hits = 0
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                if self.map[row][col] == Grid.SPACE["hit"]:
                    hits += 1

        return 1 if hits == 17 else 0
