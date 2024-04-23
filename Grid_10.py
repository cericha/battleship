from copy import deepcopy

class Grid:
    SPACE = {
        'empty' : 0,
        'miss' : -1,
        'hit' : 1
    }
    
    def __init__(self, rows: int = 10, cols: int = 10):
       self.rows = rows
       self.cols = cols
       self.map = [[self.SPACE["empty"] for x in range(rows)] for y in range(cols)]
    

    def clone(self):
        gridCopy = Grid(self.rows, self.cols)
        gridCopy.map = deepcopy(self.map)

        return gridCopy