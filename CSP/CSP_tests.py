from CSP.CSP_AI import Assignment, SHIP_LABELS, VARIABLES, DOMAIN
from Grid_10 import Grid
from Ship_10 import Ship
from Displayer_10 import Displayer

TIMES_TO_RUN = 100

displayer = Displayer()



# Adjusted version of one that is present in game manager
def place_ship(
        self, ship: Ship, row: int, col: int, direction, board: Grid
    ) -> bool:
        """
        Puts pointers to the given ship on some board Grid
        """
        ship_coords = []
        # Location is for the head of the ship
        if direction == 'horizontal':
            if col + ship.size > self.cols:
                return False
            for i in range(0, ship.size):
                new_col = col + i
                if board.map[row][new_col]:
                    return False
                ship_coords.append((row, new_col))

        elif direction == 'vertical':
            if row + ship.size > self.rows:
                return False
            for i in range(0, ship.size):
                new_row = row + i
                if board.map[new_row][col]:
                    return False
                ship_coords.append((new_row, col))

        for x, y in ship_coords:
            board.map[x][y] = ship

        return True



def show_coords(value_list):
    pretend_board = Grid()
    for x,y,v in value_list:
        pretend_board.map[y][x] = 'X'
    displayer.display(pretend_board)
def show_ship(ship, value):
    pretend_board = Grid()
    size = int(ship[1])
    x,y,v = value
    if v == True:
        for i in range(size):
            pretend_board.map[y+i][x] = 1
    else:
        for i in range(size):
            pretend_board.map[y][x-i] = 1
    displayer.display(pretend_board)