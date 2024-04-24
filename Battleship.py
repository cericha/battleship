import random
import time
from enum import Enum
from typing import List, Optional  # For below python 3.10 support

from Displayer_10 import Displayer
from Grid_10 import Grid
from Metrics_10 import Metrics
from PlayerAI_10 import PlayerAI


class Ship:
    def __init__(self, size: int, name: str) -> None:
        self.name = name
        self.size = size
        self.life = size

    def hit(self) -> str:
        self.life -= 1
        if self.life == 0:
            return "sunk"
        else:
            return "hit"

    def __hash__(self) -> int:
        return hash(self.name)


class Direction(Enum):
    VERTICAL = 1
    HORIZONTAL = 2


class GameManager:
    def __init__(
        self,
        ships: List[Ship],
        rows: int = 10,
        cols: int = 10,
        playerAI: Optional[PlayerAI] = None,
        displayer: Optional[Displayer] = None,
        timeLimit: int = -1,
    ) -> None:
        self.rows = rows
        self.cols = 10
        self.grid = Grid(rows, cols)
        self.enemy_board = self.generate_random_board()  # This makes self.fleet
        self.total_hits = 0  # With standard ships, ned
        self.needed_hits = sum([ship.size for ship in ships])
        self.over = False

        self.playerAI = playerAI or PlayerAI()
        self.displayer = displayer or Displayer()
        self.timeLimit = timeLimit

    def updateAlarm(self) -> None:
        if time.process_time() - self.prevTime > self.timeLimit:
            self.over = True
        self.prevTime = time.process_time()

    def start(self) -> Metrics:
        """
        Starts the game and goes until completion or failure
        """

        # # Initialize the game
        self.enemy_board = Grid()
        self.place_random_ships(self.enemy_board)
        self.displayer.display(self.grid)
        self.displayer.display(self.enemy_board)
        moves = 0
        while self.total_hits < self.needed_hits and not self.over:
            self.prevTime = time.process_time()
            gridCopy = self.grid.clone()  # To ensure AI cant steal this?
            moves += 1
            x, y = self.playerAI.getMove(gridCopy)
            print(f"{' ' * 6}MOVES {moves}")
            if moves > 150:
                print("Something is awry.....")
                self.displayer.display(self.enemy_board)
                return Metrics(0, moves)
            self.move(x, y)
            # Comment out displayer when you need speed
            self.displayer.display(self.grid)

            # Exceeding the Time Allotted for Any Turn Terminates the Game
            self.updateAlarm()
        self.displayer.display(self.enemy_board)
        return Metrics(0, -1)

    def move(self, x: int, y: int) -> str:
        if self.grid.map[y][x] != Grid.SPACE["empty"]:
            print("ERROR")
            return "ERROR"
        else:
            # Enemy board will contain information about miss or hit
            response = self.enemy_board.map[y][x]
            if response != Grid.SPACE["empty"]:
                # Player board will show the ship object if this move results in a sink
                self.grid.map[y][x] = (
                    response if response.hit() == "sunk" else Grid.SPACE["hit"]
                )
                self.total_hits += 1
                return "hit"  # assuming response is a pointer to a ship
            self.grid.map[y][x] = Grid.SPACE["miss"]
            return "miss"

    def generate_random_board(self) -> Grid:
        enemy_board = Grid()
        self.place_random_ships(enemy_board)
        return enemy_board

    def place_ship(
        self, ship: Ship, row: int, col: int, direction: Direction, board: Grid
    ) -> bool:
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
            # else we have valid ship placement
            for i in range(0, ship.size):
                board.map[row][col + i] = ship
        elif direction == Direction.VERTICAL:
            if row + ship.size > self.rows:
                return False

            for i in range(0, ship.size):
                if board.map[row + i][col]:
                    return False
            # else we have valid ship placement
            for i in range(0, ship.size):
                board.map[row + i][col] = ship
        return True

    def place_random_ships(self, board: Grid) -> None:
        fleet = [Ship(5, "5"), Ship(4, "4"), Ship(3, "3"), Ship(3, "3"), Ship(2, "2")]
        self.fleet = []
        while fleet:
            ship = random.choice(fleet)
            x, y = random.randint(0, 9), random.randint(0, 9)
            orientation = random.choice(list(Direction))
            placed = self.place_ship(ship, y, x, orientation, board)
            if placed:
                self.fleet.append(ship)
                fleet.remove(ship)
        print(fleet)


def main() -> None:
    playerAI = PlayerAI()
    displayer = Displayer()
    standard_fleet = [
        Ship(5, "5"),
        Ship(4, "4"),
        Ship(3, "3"),
        Ship(3, "3"),
        Ship(2, "2"),
    ]
    gameManager = GameManager(standard_fleet, 10, 10, playerAI, displayer, 0.25)
    gameManager.start()


if __name__ == "__main__":
    main()
