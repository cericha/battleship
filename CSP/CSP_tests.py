from CSP.CSP_AI import Assignment, VARIABLES, DOMAIN
from Grid_10 import Grid
from Ship_10 import Ship
from Displayer_10 import Displayer
from CSP.CSP_helper import get_full_ship_coords

class Testing:
    displayer = Displayer()
    edge_board1 = Grid()
    edge_ships1 = {
        'S5' : (5,5, False),
        'S4' : (3,6, False),
        'S31' : (2,7, False),
        'S32' : (3,9, False),
        'S2' : (3,1, False)
    }

    edge_board2 = Grid()
    edge_ships2 = {
        'S5' : (6,1, True),
        'S4' : (6,6, True),
        'S31' : (5,6, True),
        'S32' : (4,6, True),
        'S2' : (1,0, False)
    }


    def __init__(self):
        # Place ships for the edge boards
        for ship in self.edge_ships1.keys():
            self.place_ship(Ship(int(ship[1]), ship[1]), self.edge_ships1[ship], self.edge_board1)
        for ship in self.edge_ships2.keys():
            self.place_ship(Ship(int(ship[1]), ship[1]), self.edge_ships2[ship], self.edge_board2)
        
    # Adjusted version of one that is present in game manager
    def place_ship(
            self, ship: Ship, value, board: Grid
        ) -> bool:
            """
            Puts pointers to the given ship on some board Grid
            """
            print(ship.size)
            print(ship.name)
            print(value)
            ship_coords = get_full_ship_coords(value, ship.size)
            
            for x, y in ship_coords:
                board.map[y][x] = ship

            return True

    def show_coords(self, value_list):
        pretend_board = Grid()
        for x,y,v in value_list:
            pretend_board.map[y][x] = 'X'
        self.displayer.display(pretend_board)
    def show_ship(self, ship, value):
        pretend_board = Grid()
        size = int(ship[1])
        x,y,v = value
        if v == True:
            for i in range(size):
                pretend_board.map[y+i][x] = 1
        else:
            for i in range(size):
                pretend_board.map[y][x-i] = 1
        self.displayer.display(pretend_board)