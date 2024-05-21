import json
import multiprocessing
import random
import sys
import time
import resource
from typing import List, Optional  # For below python 3.10 support

from Graphs import make_statistics_graphs
from Displayer_10 import Displayer
from Grid_10 import Grid
from Metrics_10 import Metrics
from PlayerAI_10 import BaselineAI
from PlayerAI_10 import DeepAI
from Ship_10 import Ship, Direction
from Timer_10 import Timer

class GameManager:
    def __init__(
        self,
        ships: List[Ship],
        rows: int = 10,
        cols: int = 10,
        playerAI=None,
        displayer: Optional[Displayer] = None,
        timer: Optional[Timer] = None,
        show_enemy_board: bool = True,
        replay: int = 1,
    ) -> None:
        self.rows = rows
        self.cols = cols
        self.ships = ships
        self.enemyDisplay = show_enemy_board
        self.playerAI = playerAI or BaselineAI
        self.displayer = displayer or Displayer()
        self.timer = timer or Timer()  # Default initialization is infinite time
        self.replay = replay

    def start(self) -> Metrics:
        self.grid = Grid(self.rows, self.cols)
        self.enemy_board = self.generate_random_board()
        # # TODO: remove/comment out testing code if not testing edge cases
        # from CSP.CSP_tests import Testing
        # self.enemy_board = Testing()
        # self.enemy_board = self.enemy_board.edge_board2
        self.total_hits = 0
        self.needed_hits = sum([ship.size for ship in self.ships])
        self.over = False

        metrics = self.run_game()
        return metrics

    def run_game(self) -> Metrics:
        """
        Starts the game and goes until completion or failure
        """
        start_time = time.time()
        individual_move_times = []
        # # Initialize the game
        # self.displayer.display(self.grid)
        if self.enemyDisplay:
            self.displayer.display(self.enemy_board)
        moves = 0
        while self.total_hits < self.needed_hits and not self.over:
            self.timer.start_timer()
            gridCopy = self.grid.clone()  # To ensure AI cant steal this?
            moves += 1
            x, y = self.playerAI.get_move(gridCopy)
            # print(f"{' ' * 6}MOVES {moves}")
            if moves > 150:
                print("Something is awry.....")
                self.displayer.display(self.enemy_board)
                return Metrics(self.enemy_board, end_time-start_time, individual_move_times, self.get_max_ram_usage())
            start_time_move = time.time()
            self.make_move(x, y)
            end_time_move = time.time()
            # storing time taken for move
            individual_move_times.append((moves, end_time_move-start_time_move))
            # Comment out displayer when you need speed
            self.displayer.display(self.grid)

            # Exceeding the Time Allotted for Any Turn Terminates the Game
            self.over = self.timer.is_time_up()
        if self.over:
            print("Game Over - Ran out of time!")
        end_time = time.time()
        # print("Original Enemy Board:")
        self.displayer.display(self.enemy_board)
        return Metrics(self.enemy_board, end_time-start_time, individual_move_times, self.get_max_ram_usage())

    def make_move(self, x: int, y: int) -> str:
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

    # Function to get max RAM usage in megabytes
    def get_max_ram_usage(self):
        # Documentation only lists things as being reported in bytes, so to convert we divide by 1024^2
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        return usage / (1024 * 1024)

# PARALLEL SIMULATION TESTING

def run_simulation(strategy, allowed_time, standard_fleet, rows, columns, displayer, show_enemy_board):
    timer = Timer(allowed_time)
    playerAI = get_player_strategy(strategy)
    gameManager = GameManager(
        standard_fleet, rows, columns, playerAI, displayer, timer, show_enemy_board
    )
    # Start game
    game_metrics = gameManager.start()
    return game_metrics

def run_simulations_in_parallel(strategy, allowed_time, standard_fleet, rows, columns, displayer, show_enemy_board, times_to_run, num_processes=None):
    with multiprocessing.Pool(processes=num_processes) as pool:
        results = [pool.apply_async(run_simulation, (strategy, allowed_time, standard_fleet, rows, columns, displayer, show_enemy_board)) for _ in range(times_to_run)]
        all_game_metrics = [result.get() for result in results]
    return all_game_metrics

# END PARALLEL SIMULATION TESTING


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
    strategy = config["strategy"]
    rows = config["board"]["rows"]
    columns = config["board"]["columns"]
    displayer_on = config["displayer"]["display"]
    show_enemy_board = config["displayer"]["show_enemy_board"]
    times_to_run = config["times_to_run"]

    # playerAI = get_player_strategy(strategy)

    displayer = Displayer(displayer_on)
    cores_to_use = 6
    # Initialize game objects
    start_time = time.time()
    all_game_metrics = run_simulations_in_parallel(
        strategy, allowed_time, standard_fleet, rows, columns,
        displayer, show_enemy_board, times_to_run, num_processes=cores_to_use)
    end_time = time.time()
    print(f'Running {times_to_run} simulations took {str(end_time-start_time)} seconds to run using {cores_to_use} cores')

    total_time_average = 0
    total_move_average = 0
    max_ram_usage_average = 0
    for game in all_game_metrics:
        total_time_average += game.total_running_time
        total_move_average += game.total_moves
        max_ram_usage_average += game.max_ram_usage
    total_time_average = total_time_average / times_to_run
    total_move_average = total_move_average / times_to_run
    max_ram_usage_average = max_ram_usage_average / times_to_run
    print(f'Average metrics over {times_to_run} games:')
    print(f'total_time_average: {total_time_average}')
    print(f'total_move_average: {total_move_average}')
    print(f'max_ram_usage_average: {max_ram_usage_average}')
    make_statistics_graphs(all_game_metrics)

def get_player_strategy(strategy):

    # Initialize movement strategy
    if strategy == "human":
        from PlayerAI_10 import HumanPlayer

        return HumanPlayer()
    elif strategy == "baseline":
        from PlayerAI_10 import BaselineAI


        return BaselineAI()
    elif strategy == "csp":
        from CSP.CSP_AI import CSPAI
        return CSPAI()

    elif strategy == "deep":
        from PlayerAI_10 import DeepAI

        playerAI = DeepAI()
    else:
        print(f"Unknown movement strategy given {strategy}")
        exit(1)

if __name__ == "__main__":
    main()
