import random
from typing import List, Tuple, Set, Optional  # For below python 3.10 support
from copy import deepcopy

from Displayer_10 import Displayer
from Grid_10 import Grid
from Metrics_10 import Metrics
from PlayerAI_10 import PlayerAI
from Ship_10 import Ship, Direction
from Timer_10 import Timer


class GameManager:
    def __init__(
        self,
        ships: Set[Ship],
        rows: int = 10,
        cols: int = 10,
        playerAI: Optional[PlayerAI] = None,
        displayer: Optional[Displayer] = None,
        timer: Optional[Timer] = None,
    ) -> None:
        self.ships = deepcopy(ships)
        self.rows = rows
        self.cols = cols
        self.grid = Grid(rows, cols)
        self.total_hits = 0  # With standard ships, ned
        self.needed_hits = sum([ship.size for ship in ships])
        self.over = False

        self.enemy_board = self.initialize_game_board()  # This makes self.fleet

        self.playerAI = playerAI or PlayerAI()
        self.displayer = displayer or Displayer()
        self.timer = timer or Timer()  # Default initialization is infinite time

    def start(self) -> Metrics:
        """
        Starts the game and goes until completion or failure
        """

        # # Initialize the game
        self.enemy_board = Grid()
        self.deploy_random_fleet(self.enemy_board, self.ships)
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

    def initialize_game_board(self, fleet=None) -> Grid:
        # fleet should take on list[Tuple[ship, Tuple[int, int]]] or [(ship1, coord1), (ship2, coord2)]

        enemy_board = Grid()
        if fleet is None:
            self.deploy_random_fleet(enemy_board, self.ships)
        else:
            for ship, ship_coords in fleet:
                self.place_ship(ship, ship_coords, enemy_board)

        return enemy_board

    def generate_ship_placement(
        self, ship: Ship, row: int, col: int, direction: Direction
    ):
        ship_coords = []
        if direction == Direction.HORIZONTAL:
            if col + ship.size > self.cols:
                return False, ship_coords
            ship_coords = [(row, col + i) for i in range(ship.size)]

        elif direction == Direction.VERTICAL:
            if row + ship.size > self.rows:
                return False, ship_coords
            ship_coords = [(row + i, col) for i in range(ship.size)]
        return True, ship_coords

    def can_place_ship(
        self, ship: Ship, row: int, col: int, direction: Direction, board: Grid
    ) -> Tuple[bool, List[Tuple[int, int]]]:
        ship_coords = []
        if board.map[row][col] != Grid.SPACE["empty"]:
            return False, ship_coords

        in_bounds, ship_coords = self.generate_ship_placement(ship, row, col, direction)

        if not in_bounds or any(board.map[x][y] for x, y in ship_coords):
            return False, ship_coords

        return True, ship_coords

    def place_ship(
        self, ship: Ship, ship_coords: list[Tuple[int, int]], board: Grid
    ) -> bool:
        for x, y in ship_coords:
            board.map[x][y] = ship
        return True

    def deploy_random_fleet(self, board: Grid, fleet: List[Ship]) -> None:
        fleet = list(deepcopy(fleet))
        self.fleet = []
        while fleet:
            ship = random.choice(fleet)
            x, y = random.randint(0, self.cols - 1), random.randint(0, self.rows - 1)
            orientation = random.choice(list(Direction))

            placeable, ship_coords = self.can_place_ship(ship, y, x, orientation, board)

            if not placeable:
                continue

            self.place_ship(ship, ship_coords, board)
            self.fleet.append(ship)
            fleet.remove(ship)


def main() -> None:
    playerAI = PlayerAI()
    displayer = Displayer()
    timer = Timer(0.25)
    standard_fleet = set(
        [
            Ship(5, "5"),
            Ship(4, "4"),
            Ship(3, "3"),
            Ship(3, "3"),
            Ship(2, "2"),
        ]
    )
    gameManager = GameManager(standard_fleet, 10, 10, playerAI, displayer, timer)
    gameManager.start()


if __name__ == "__main__":
    main()
