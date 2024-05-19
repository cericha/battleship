import random
from typing import Tuple
from Grid_10 import Grid
import math
from copy import deepcopy
from itertools import product
from Ship_10 import Direction


class Grid_D:
    """
    Remember, when accessing the arary, it is of form grid.map[y][x], NOT grid.map[x][y]
    """

    SPACE = {"empty": 0, "miss": "X", "hit": 1, "potential_ship": 2}

    def __init__(self, rows: int = 10, cols: int = 10) -> None:
        self.rows = rows
        self.cols = cols
        self.map = [[self.SPACE["empty"] for x in range(cols)] for y in range(rows)]

    def getEmptySpaces(self) -> Tuple[int, int]:
        empty_spaces = []
        for y in range(self.rows):
            for x in range(self.cols):
                if self.map[y][x] == self.SPACE["empty"]:
                    empty_spaces.append((x, y))
        return empty_spaces

    def clone(self) -> "Grid_D":
        gridCopy = Grid_D(self.rows, self.cols)
        gridCopy.map = deepcopy(self.map)

        return gridCopy

    def get_result(self, player):
        # Implement logic to determine the result of the game from this player's perspective
        hits = 0
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                if self.map[row][col] == Grid_D.SPACE["hit"]:
                    hits += 1

        return 1 if hits == 17 else 0

    @classmethod
    def from_grid(cls, grid: Grid) -> "Grid_D":
        grid_d = cls(grid.rows, grid.cols)
        grid_d.map = deepcopy(grid.map)
        return grid_d


class MoveStrategy:

    def __init__(self):
        self.prev_move = None

    def get_prev_move_result(self, board: Grid):
        if self.prev_move == None:
            return "Have not made a move yet"
        x, y = self.prev_move
        if board.map[y][x] == Grid.SPACE["empty"]:
            return f"x:{x} y:{y} has not been fired on"
        elif board.map[y][x] == Grid.SPACE["miss"]:
            return "miss"
        else:
            return "hit"

    def get_move(self, move: str) -> Tuple[int, int]:
        """
        make sure to set self.prev_move to whatever move you determine
        """
        pass


class HumanPlayer(MoveStrategy):

    def parse_move(self, move: str) -> Tuple[int, int]:
        return tuple(map(int, str(move).split(" ")))

    def get_move(self, board: Grid):
        move = input("Enter next move: ")
        return self.parse_move(move)


class BaselineAI(MoveStrategy):

    def get_move(self, board: Grid):
        choices = board.getEmptySpaces()
        choice = random.choice(choices)
        # save prev move, just assuming after this function we call make_move
        self.prev_move = choice
        return (0, 0) if len(choices) == 0 else choice


class BaselineAISmarter(MoveStrategy):

    def __init__(self):
        super().__init__()
        self.available_spaces = [(x, y) for x in range(10) for y in range(10)]

    def get_move(self, board: Grid):
        x, y = random.choice(self.available_spaces)
        self.available_spaces.remove((x, y))
        return (x, y)


class Node:
    def __init__(self, state: Grid_D, parent: "Node", move: Tuple[int, int]):
        self.state = state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.value = 0
        self.action = move

    def add_child(self, child):
        self.children.append(child)

    def is_fully_expanded(self):
        all_legal_moves = self.state.getEmptySpaces()
        return len(self.children) == len(all_legal_moves)

    def update(self, value):
        self.value += value


class ISMCTS(MoveStrategy):

    def __init__(self, simulations: int = 100):
        super().__init__()
        self.simulations = simulations
        self.ship_sizes = [5, 4, 3, 3, 2]  # Fix later to instantiate directly

    def get_move(self, board: Grid_D):
        simulation_board = Grid_D.from_grid(board)
        simulation_board = deepcopy(board)
        new_board = self.SO_ISMCTS(simulation_board, self.simulations)
        for row in new_board.state.map:
            print(row)
        return new_board.action

    def UCT_select_best_child(self, node, C=0.7):
        best_value = float("-inf")
        best_nodes = []
        for child in node.children:
            if child.visits == 0:
                uct_value = float("inf")
            else:
                uct_value = (child.value / child.visits) + C * math.sqrt(
                    math.log(node.visits) / child.visits
                )
            if uct_value > best_value:
                best_value = uct_value
                best_nodes = [child]
            elif uct_value == best_value:
                best_nodes.append(child)

        # Why would it be zero? TODO - Check for and fix this case
        if len(best_nodes) == 0:
            return node
        return random.choice(best_nodes)

    def SELECT(self, v: Node, d: Grid_D):
        while not self.is_terminal(v):
            if v.is_fully_expanded():
                v = self.UCT_select_best_child(v)
                d = self.apply_action(d, v.action)
            else:
                break
        return v, d

    def EXPAND(self, new_state: Node, new_determ: Grid_D):
        legal_moves = self.get_legal_moves(new_determ)
        move_x, move_y = random.choice(list(legal_moves))
        new_determ = deepcopy(new_determ)

        if new_determ.map[move_y][move_x] == Grid_D.SPACE["potential_ship"]:
            new_determ.map[move_y][move_x] = Grid_D.SPACE["hit"]
        else:
            new_determ.map[move_y][move_x] = Grid_D.SPACE["miss"]

        child_state = Node(new_determ, new_state, move=(move_x, move_y))
        new_state.add_child(child_state)
        child_state.parent = new_state

        return child_state, new_determ

    def SIMULATE(self, d: Grid_D):
        simulation_state = deepcopy(d)
        legal_moves = self.get_legal_moves(simulation_state)
        total_hits = sum(
            cell == Grid_D.SPACE["hit"] for row in simulation_state.map for cell in row
        )
        while len(legal_moves) > 0 and total_hits < 17:
            move = random.choice(list(legal_moves))
            legal_moves.remove(move)
            x, y = move
            if simulation_state.map[y][x] == Grid_D.SPACE["empty"]:
                simulation_state.map[y][x] = Grid_D.SPACE["miss"]
            elif simulation_state.map[y][x] == Grid_D.SPACE["potential_ship"]:
                simulation_state.map[y][x] = Grid_D.SPACE["hit"]
                total_hits += 1
        return len(legal_moves) + 1

    def BACKPROPAGATE(self, r: float, v: Node):
        # This does not follow I think correctly Information Set MCTS backpropogate
        while v is not None:
            v.update(r)
            v = v.parent

    def SO_ISMCTS(self, current_board, n: int = 1000):

        root_node = Node(current_board, None, None)
        for _ in range(n):
            new_determinization = generate_valid_configuration(
                current_board, self.ship_sizes, 1000
            )
            new_state, new_determ = self.SELECT(root_node, new_determinization)
            if not self.is_terminal(new_state):
                new_state, new_determ = self.EXPAND(new_state, new_determ)
            reward = self.SIMULATE(new_determ)
            self.BACKPROPAGATE(reward, new_state)

        return max(root_node.children, key=lambda c: c.visits)

    def get_legal_moves(self, state: Grid_D):
        open_cells = state.getEmptySpaces()
        legal_moves = set(open_cells)
        return legal_moves
        # TO DO - Implement it such that open LEGAL cells are available...
        # for cell in open_cells:
        #     if self.can_fit_remaining_ships(state, cell):
        #         legal_moves.append(cell)

    def apply_action(self, state: Grid_D, action: Tuple[int, int]) -> Grid_D:
        x, y = action
        if state.map[y][x] == Grid_D.SPACE["potential_ship"]:
            state.map[y][x] = Grid_D.SPACE["hit"]
        else:
            state.map[y][x] = Grid_D.SPACE["miss"]
        return state

    def is_terminal(self, state: Node):
        total_ship_segments = sum(self.ship_sizes)
        hit_count = sum(
            cell == Grid_D.SPACE["hit"] for row in state.state.map for cell in row
        )
        return hit_count == total_ship_segments


def can_place_ship(grid, ship_size, x, y, direction):
    if direction == Direction.HORIZONTAL:
        if x + ship_size > grid.cols:
            return False
        for i in range(ship_size):
            # print(grid.map[y][x + 1])
            if grid.map[y][x + i] == Grid_D.SPACE["miss"]:
                return False
    elif direction == Direction.VERTICAL:
        if y + ship_size > grid.rows:
            return False
        for i in range(ship_size):
            if grid.map[y + i][x] == Grid_D.SPACE["miss"]:
                return False
    return True


def find_valid_placements(grid, ship_size):
    valid_placements = []
    for y in range(grid.rows):
        for x in range(grid.cols):
            if can_place_ship(grid, ship_size, x, y, Direction.HORIZONTAL):
                valid_placements.append((x, y, Direction.HORIZONTAL))
            if can_place_ship(grid, ship_size, x, y, Direction.VERTICAL):
                valid_placements.append((x, y, Direction.VERTICAL))
    return valid_placements


def generate_all_configurations(grid, ship_sizes):
    all_placements = [
        find_valid_placements(grid, ship_size) for ship_size in ship_sizes
    ]
    all_combinations = list(product(*all_placements))
    print(len(all_combinations))

    valid_configurations = []
    for combination in all_combinations:
        new_grid = deepcopy(grid)
        valid = True
        for (x, y, direction), ship_size in zip(combination, ship_sizes):
            if can_place_ship(new_grid, ship_size, x, y, direction):
                place_ship(
                    new_grid, ship_size, x, y, direction, Grid_D.SPACE["potential_ship"]
                )
            else:
                valid = False
                break
        if valid:
            valid_configurations.append(new_grid)
            if len(valid_configurations) > 100:
                return valid_configurations
    return valid_configurations


def matches_hits(grid, original_grid):
    for y in range(grid.rows):
        for x in range(grid.cols):
            if (
                original_grid.map[y][x] == Grid_D.SPACE["hit"]
                and grid.map[y][x] != Grid_D.SPACE["potential_ship"]
            ):
                return False
    return True


def place_ship(grid, ship_size, x, y, direction, place_ship_enum):
    # Does not account for accidently replacing a "hit"
    if direction == Direction.HORIZONTAL:
        for i in range(ship_size):
            grid.map[y][x + i] = place_ship_enum
    elif direction == Direction.VERTICAL:
        for i in range(ship_size):
            grid.map[y + i][x] = place_ship_enum


def generate_random_determinization(state: Grid_D, ship_sizes: list) -> Grid_D:
    grid = deepcopy(state)
    random.shuffle(ship_sizes)
    count = 0
    for index, ship_size in enumerate(ship_sizes):
        placed = False
        while not placed:
            count += 1
            x = random.randint(0, grid.cols - 1)
            y = random.randint(0, grid.rows - 1)
            direction = random.choice(list(Direction))
            if can_place_ship(grid, ship_size, x, y, direction):
                place_ship(
                    grid, ship_size, x, y, direction, Grid_D.SPACE["potential_ship"]
                )
                placed = True
            if count % 1000000 == 0:
                print(count)
                valid_configurations = generate_all_configurations(state, ship_sizes)
                matching_configurations = [
                    config
                    for config in valid_configurations
                    if matches_hits(config, state)
                ]
                if not matching_configurations:
                    print("ERROR")
                    exit(1)
                    return None
                return random.choice(matching_configurations)
    return grid


def generate_valid_configuration(
    state: Grid_D, ship_sizes: list, threshold: int
) -> Grid_D:
    all_placements = [
        find_valid_placements(state, ship_size) for ship_size in ship_sizes
    ]
    total_combinations = 1
    for placements in all_placements:
        total_combinations *= len(placements)

    if total_combinations <= threshold:
        valid_configurations = generate_all_configurations(state, ship_sizes)
        matching_configurations = [
            config for config in valid_configurations if matches_hits(config, state)
        ]
        if not matching_configurations:
            print("ERROR")
            exit(1)
            return None
        return random.choice(matching_configurations)
    else:
        return generate_random_determinization(state, ship_sizes)
