from copy import deepcopy

class Grid:
    """
    Remember, when accessing the arary, it is of form grid.map[y][x], NOT grid.map[x][y]
    """
    SPACE = {
        'empty' : 0,
        'miss' : 'X',
        'hit' : 1
    }
    
    def __init__(self, rows: int = 10, cols: int = 10):
       self.rows = rows
       self.cols = cols
       self.map = [[self.SPACE["empty"] for x in range(cols)] for y in range(rows)]
    
    def getEmptySpaces(self):
        empty_spaces = []
        for y in range(self.rows):
            for x in range(self.cols):
                if self.map[y][x] == self.SPACE['empty']:
                    empty_spaces.append((x, y))
        return empty_spaces
    def clone(self):
        gridCopy = Grid(self.rows, self.cols)
        gridCopy.map = deepcopy(self.map)

        return gridCopy