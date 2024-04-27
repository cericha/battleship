import json
import random
import sys
from typing import List, Optional  # For below python 3.10 support

from Displayer_10 import Displayer
from Grid_10 import Grid
from Metrics_10 import Metrics
from PlayerAI_10 import PlayerAI
from Ship_10 import Ship, Direction
from Timer_10 import Timer


class GameManager:
    def __init__(
        self,
        ships: List[Ship],
        rows: int = 10,
        cols: int = 10,
        playerAI: Optional[PlayerAI] = None,
        displayer: Optional[Displayer] = None,
        timer: Optional[Timer] = None,
    ) -> None:
        self.rows = rows
        self.cols = cols
        self.grid = Grid(rows, cols)
        self.enemy_board = self.generate_random_board()  # This makes self.fleet
        self.total_hits = 0  # With standard ships, ned
        self.needed_hits = sum([ship.size for ship in ships])
        self.over = False

        self.playerAI = playerAI or PlayerAI()
        self.displayer = displayer or Displayer()
        self.timer = timer or Timer()  # Default initialization is infinite time

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
            self.timer.start_timer()
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
            self.over = self.timer.is_time_up()
        if self.over:
            print("Game Over - Ran out of time!")
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
        ship_coords = []
        # Location is for the head of the ship
        if direction == Direction.HORIZONTAL:
            if col + ship.size > self.cols:
                return False
            for i in range(0, ship.size):
                new_col = col + i
                if board.map[row][new_col]:
                    return False
                ship_coords.append((row, new_col))

        elif direction == Direction.VERTICAL:
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
    # Parse input
    if len(sys.argv) == 1:
        configuration_path = "standard_game.json"
    elif len(sys.argv) == 2:
        configuration_path = sys.argv[1]
    else:
        print("Error: Incorrect number of arguments.")
        exit(1)

    # Initialize configuration file
    try:
        with open(configuration_path, "r") as file:
            config = json.load(file)
    except Exception as e:
        print(e)
        exit(1)

    # Load default values
    ships = config["ships"]
    standard_fleet = [Ship(s["size"], s["name"]) for s in ships]
    allowed_time = float(config["timer"]["timeout"])
    player_or_ai = config["player"]
    rows = config["board"]["rows"]
    columns = config["board"]["columns"]

    # Instantiate game objects
    playerAI = PlayerAI()
    displayer = Displayer()  # TODO - Add flag to not display enemy board to config
    timer = Timer(allowed_time)
    gameManager = GameManager(standard_fleet, rows, columns, playerAI, displayer, timer)

    # Start game
    gameManager.start()


if __name__ == "__main__":
    main()
