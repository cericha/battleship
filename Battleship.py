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
        self.enemy_board = self.generate_random_board(self.grid) # This makes self.fleet
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
        self.place_random_ships(self.grid)
        self.displayer.display(self.grid)
        while self.total_hits < 17 and not self.over:
            self.prevTime = time.process_time()
            gridCopy = self.grid.clone() # To ensure AI cant steal this?
            
            x, y = self.player.getMove(gridCopy) # Player board should be not original board... good call
            
            self.move(x, y)
            # Comment out displayer when you need speed
            self.displayer.display(self.grid)

            # Exceeding the Time Allotted for Any Turn Terminates the Game
            self.updateAlarm()
        return Metrics(0,-1)



    def move(self, x, y) -> str:
        if self.grid[x][y] != Grid.SPACE['empty']:
            return 'ERROR'
        else:
            # Enemy board will contain information about miss or hit
            response = self.enemy_board[x][y]
            if response != Grid.SPACE['empty']:
                # Player board will show the ship object if this move results in a sink
                self.grid[x][y] = response if response.hit() == 'sunk' else Grid.SPACE['hit']
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
                if board[row][col + i]:
                    return False
            else:
                for i in range(0, ship.size):
                    board[row][col + i] = ship
        elif direction == Direction.VERTICAL:
            if row + ship.size > self.rows:
                return False
            for i in range(0, ship.size):
                if self.grid[row + i][col]:
                    return False
            else:
                for i in range(0, ship.size):
                    board[row + i][col] = ship

        return True

    def place_random_ships(self, board: Grid) -> None:
        fleet = [Ship(5), Ship(4), Ship(3), Ship(3), Ship(2)]
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
        for row in self.grid:
            display_row = [1 if x else 0 for x in row]
            print(display_row)


    standard_fleet = [Ship(5), Ship(4), Ship(3), Ship(3), Ship(2)]
standard_fleetm,

def main():
    playerAI    = PlayerAI()
    displayer   = Displayer()
    gameManager = GameManager(10, 10, playerAI, displayer, 0.25)
    game     = gameManager.start()

if __name__ == '__main__':
    main()



# class GameManager:
#     SPACE = {
#         'empty' : 0,
#         'miss' : -1,
#         'hit' : 1,
#     }
#     
#     def __init__(self, rows = 10, cols = 10, playerAI=None, displayer=None):
# 
#     def updateAlarm(self) -> None:
#         raise NotImplemented
#     
#     def fire_on(self, x, y) -> str:
#         raise NotImplemented
#     
#     def place_random_ships(self, grid) -> Grid:
#         raise NotImplemented
#         
#     def start(self) -> int:
#         """ Main method that handles running the game of 2048 """
#         
#         # Initialize the game
#         self.place_random_ships(self.grid)
#         self.displayer.display(self.grid)
# 
#         # TODO: Below not worked on yet
#         self.prevTime = time.process_time()
# 
#         while self.grid.canMove() and not self.over:
#             # Copy to Ensure AI Cannot Change the Real Grid to Cheat
#             gridCopy = self.grid.clone()
# 
#             move = None
# 
#             if turn == PLAYER_TURN:
#                 print("Player's Turn: ", end="")
#                 move = self.playerAI.getMove(gridCopy)
#                 
#                 print(actionDic[move])
# 
#                 # If move is valid, attempt to move the grid
#                 if move != None and 0 <= move < 4:
#                     if self.grid.canMove([move]):
#                         self.grid.move(move)
# 
#                     else:
#                         print("Invalid PlayerAI Move - Cannot move")
#                         self.over = True
#                 else:
#                     print("Invalid PlayerAI Move - Invalid input")
#                     self.over = True
#             else:
#                 print("Computer's turn: ")
#                 move = self.computerAI.getMove(gridCopy)
# 
#                 # Validate Move
#                 if move and self.grid.canInsert(move):
#                     self.grid.setCellValue(move, self.getNewTileValue())
#                 else:
#                     print("Invalid Computer AI Move")
#                     self.over = True
# 
#             # Comment out during heuristing optimizations to increase runtimes.
#             # Printing slows down computation time.
#             self.displayer.display(self.grid)
# 
#             # Exceeding the Time Allotted for Any Turn Terminates the Game
#             self.updateAlarm()
#             turn = 1 - turn
# 
#         return self.grid.getMaxTile()
# 
# start = time.perf_counter()
# for i in range(0, 153300):
#     game = Game()
#     game.place_random_ships()
# end = time.perf_counter()
# for row in board2:
#     print(row)

# big = max(x for row in board2 for x in row)
# small = min(x for row in board2 for x in row)
# logthing = math.log(big - small, math.sqrt(big - small))
# print(logthing)
# for i in range(0, 10):
#     for j in range(0, 10):
#         board2[i][j] = int(math.log(board2[i][j], logthing))
#     print(board2[i])

# for i in range(0, 10):
#     for j in range(0, 10):
#         board2[i][j] = int(board2[i][j] / 1000)
#     print(board2[i])
# print("Total Time:", end - start, "seconds")
