from enum import Enum
import random
import time

class Ship:
    def __init__(self, size):
        self.size = size

class Carrier(Ship):
    def __init__(self):
        super().__init__(5)

class Battleship(Ship):
    def __init__(self):
        super().__init__(4)

class Destroyer(Ship):
    def __init__(self):
        super().__init__(3)

class Submarine(Ship):
    def __init__(self):
        super().__init__(3)

class PatrolBoat(Ship):
    def __init__(self):
        super().__init__(2)

class Direction(Enum):
    VERTICAL = 1
    HORIZONTAL = 2


board2 = [[0 for x in range(10)] for y in range(10)]

class Game:
    ROWS = 10
    COLUMNS = 10

    def __init__(self) -> None:
        self.board = [[False for x in range(Game.ROWS)] for y in range(Game.COLUMNS)]
    
    def move(self, x, y) -> str:
        if self.board[x][y]:
            self.board[x][y] = 'X'
            return True
        else:
            self.board[x][y] = 'O'
            return False


    def place_ship(self, ship: Ship, row: int, col: int, direction: Direction) -> bool:
        global board2
        # Location is for the head of the ship    
        if direction == Direction.HORIZONTAL:
            if col + ship.size > Game.COLUMNS:
                return False
            for i in range(0, ship.size):
                if self.board[row][col + i]:
                    return False
            else:
                for i in range(0, ship.size):
                    self.board[row][col + i] = True
                    board2[row][col + i] += 1
        elif direction == Direction.VERTICAL:
            if row + ship.size > Game.ROWS:
                return False
            for i in range(0, ship.size):
                if self.board[row + i][col]:
                    return False
            else:
                for i in range(0, ship.size):
                    self.board[row + i][col] = True
                    board2[row + i][col] += 1

        return True

    def place_random_ships(self) -> None:
        fleet = [Carrier(), Battleship(), Destroyer(), Submarine(), PatrolBoat()]
        while fleet:
            ship = random.choice(fleet)
            x, y = random.randint(0, 9), random.randint(0, 9)
            orientation = random.choice(list(Direction))
            placed = self.place_ship(ship, x, y, orientation)
            if placed:
                fleet.remove(ship)

    def print_board(self) -> None:
        for row in self.board:
            display_row = [1 if x else 0 for x in row]
            print(display_row)

start = time.perf_counter()
for i in range(0, 153300):
    game = Game()
    game.place_random_ships()
end = time.perf_counter()
for row in board2:
    print(row)
# big = max(x for row in board2 for x in row)
# small = min(x for row in board2 for x in row)
# logthing = math.log(big - small, math.sqrt(big - small))
# print(logthing)
# for i in range(0, 10):
#     for j in range(0, 10):
#         board2[i][j] = int(math.log(board2[i][j], logthing))
#     print(board2[i])
for i in range(0, 10):
    for j in range(0, 10):
        board2[i][j] = int(board2[i][j] / 1000)
    print(board2[i])
print("Total Time:", end - start, "seconds")
