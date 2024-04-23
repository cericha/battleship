from enum import Enum
import random
import time
from copy import deepcopy

from Grid_10 import Grid
from PlayerAI_10 import PlayerAI
from Displayer_10 import Displayer
from Metrics_10 import Metrics


class Ship:
    def __init__(self, size, name):
        self.name = name
        self.size = size
        self.life = size

    def hit(self):
        self.life -= 1
        if self.life == 0:
            return 'sunk'
        else:
            return 'hit'
     
    def __hash__(self):
        return hash(self.name)


class Direction(Enum):
    VERTICAL = 1
    HORIZONTAL = 2


class GameManager:

    def __init__(self, ships, rows = 10, cols = 10, playerAI=None, displayer=None, timeLimit=-1):
        self.rows = rows
        self.cols = 10
        self.grid = Grid(rows, cols)
        self.enemy_board = self.generate_random_board() # This makes self.fleet
        self.total_hits = 0 # With standard ships, ned 
        self.needed_hits = sum([ship.size for ship in ships])
        self.over = False

        self.playerAI   = playerAI   or PlayerAI()
        self.displayer  = displayer  or Displayer()
        self.timeLimit = timeLimit
 
        
    def updateAlarm(self) -> None:
        if time.process_time() - self.prevTime > self.timeLimit:
            self.over = True
        self.prevTime = time.process_time()
        
    def start(self) -> Metrics:
        """
        Starts the game and goes until completion or failure
        """
        # """ Main method that handles running the game of 2048 """
        
        # # Initialize the game
        self.enemy_board = Grid()
        self.place_random_ships(self.enemy_board)
        self.displayer.display(self.grid)
        moves = 0
        while self.total_hits < 17 and not self.over:
            self.prevTime = time.process_time()
            gridCopy = self.grid.clone() # To ensure AI cant steal this?
            moves += 1
            x, y = self.playerAI.getMove(gridCopy) # Player board should be not original board... good call
            print(f"{' ' * 6}MOVES {moves}")
            if moves > 10000:
                print("Something is awry.....")
                return Metrics(0,moves)
            self.move(x, y)
            # Comment out displayer when you need speed
            self.displayer.display(self.grid)
            #self.print_board()

            # Exceeding the Time Allotted for Any Turn Terminates the Game
            self.updateAlarm()
        return Metrics(0,-1)


    def move(self, x, y) -> str:
        if self.grid.map[x][y] != Grid.SPACE['empty']:
            return 'ERROR'
        else:
            # Enemy board will contain information about miss or hit
            response = self.enemy_board.map[x][y]
            if response != Grid.SPACE['empty']:
                # Player board will show the ship object if this move results in a sink
                self.grid.map[x][y] = response if response.hit() == 'sunk' else Grid.SPACE['hit']
                self.total_hits += 1
                return 'hit' # assuming response is a pointer to a ship
            return 'miss'

    def generate_random_board(self):
        enemy_board = Grid()
        self.place_random_ships(enemy_board)
        return enemy_board
        

    def place_ship(self, ship: Ship, row: int, col: int, direction: Direction, board: Grid) -> bool:
        """
        Puts pointers to the given ship on some board Grid
        """
        # global board2
        # Location is for the head of the ship    
        if direction == Direction.HORIZONTAL:
            if col + ship.size > self.cols:
                return False
            for i in range(0, ship.size):
                if board.map[row][col + i]:
                    return False
            else:
                for i in range(0, ship.size):
                    board.map[row][col + i] = ship
        elif direction == Direction.VERTICAL:
            if row + ship.size > self.rows:
                return False
            else:
                for i in range(0, ship.size):
                    board.map[row + i][col] = ship

        return True


    def place_random_ships(self, board: Grid) -> None:
        fleet = [Ship(5, '5'), Ship(4, '4'), Ship(3, '3'), Ship(3, '3'), Ship(2, '2')]
        self.fleet = []
        while fleet:
            ship = random.choice(fleet)
            x, y = random.randint(0, 9), random.randint(0, 9)
            orientation = random.choice(list(Direction))
            placed = self.place_ship(ship, x, y, orientation, board)
            if placed:
                self.fleet.append(ship)
                fleet.remove(ship)

    def print_board(self) -> None:

        print("AHHHH")
        for row in self.grid.map:
            display_row = [1 if x else 0 for x in row]
            print(display_row)


def main():
    playerAI    = PlayerAI()
    displayer   = Displayer()
    standard_fleet = [Ship(5, '5'), Ship(4, '4'), Ship(3, '3'), Ship(3, '3'), Ship(2, '2')]
    gameManager = GameManager(standard_fleet, 10, 10, playerAI, displayer, 0.25)
    game     = gameManager.start()

if __name__ == '__main__':
    main()

