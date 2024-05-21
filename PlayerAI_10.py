import random
from typing import Tuple
from Grid_10 import Grid
import math
from copy import deepcopy
from itertools import product
from Ship_10 import Direction, Ship
from Ship_10 import Ship

from collections import deque
import random
import math


class Grid_D:
    """Slightly different implementation of Grid class, for use with ISMCTS
    determinizations and information set
    """

    SPACE = {"empty": 0, "miss": "X", "hit": 1, "potential_ship": 7}

    def __init__(self, rows: int = 10, cols: int = 10) -> None:
        """Create a grid"""
        self.rows = rows
        self.cols = cols
        self.map = [[self.SPACE["empty"] for x in range(cols)] for y in range(rows)]

    def getEmptySpaces(self) -> Tuple[int, int]:
        """Get available spaces, with determinization, there might be a
        guessed ship location, but that is a cell not yet taken"""
        empty_spaces = []
        for y in range(self.rows):
            for x in range(self.cols):
                if (
                    self.map[y][x] == self.SPACE["empty"]
                    or self.map[y][x] == self.SPACE["potential_ship"]
                ):
                    empty_spaces.append((x, y))
        return empty_spaces

    def clone(self) -> "Grid_D":
        gridCopy = Grid_D(self.rows, self.cols)
        gridCopy.map = deepcopy(self.map)

        return gridCopy

    def get_result(self, player):
        """Get number of hits"""
        hits = 0
        for row in range(len(self.map)):
            for col in range(len(self.map[row])):
                if self.map[row][col] == Grid_D.SPACE["hit"]:
                    hits += 1

        return 1 if hits == 17 else 0

    @classmethod
    def from_grid(cls, grid: Grid) -> "Grid_D":
        """Copies from a Grid object to a Grid_D object"""
        grid_d = cls(grid.rows, grid.cols)
        grid_d.map = deepcopy(grid.map)
        for i, row in enumerate(grid_d.map):
            for j, item in enumerate(row):
                if isinstance(item, Ship):
                    grid_d.map[i][j] = 1

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
        elif board.map[y][x] == Grid.SPACE["hit"]:
            return "hit"
        else:
            return "sunk"

    def get_move(self, move: str) -> Tuple[int, int]:
        """
        make sure to set self.prev_move to whatever move you determine
        """
        pass


class HumanPlayer(MoveStrategy):

    def parse_move(self, move: str) -> Tuple[int, int]:
        # No sanitation here, easy for invalid input to fail out the function
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
    """Node class for use with ISMCTS"""

    _node_id = 0

    def __init__(self, state: Grid_D, parent: "Node", move: Tuple[int, int]):
        self.id = Node._node_id
        Node._node_id += 1
        self.state = state
        self.parent = parent
        self.children = []
        self.visits = 0
        self.value = 0
        self.action = move

    def add_child(self, child):
        self.children.append(child)

    def is_fully_expanded(self):
        """Checks to see if given a determinization in the information set if
        the current node is fully expanded (There nexist no legal moves left)"""
        all_legal_moves = self.state.getEmptySpaces()
        current_actions = set([child.action for child in self.children])
        is_expanded = len(all_legal_moves) == len(current_actions)
        return is_expanded

    def update(self, value):
        """Update value for backpropogation in MCTS"""
        self.value += value


class ISMCTS(MoveStrategy):

    def __init__(self, simulations: int = 100):
        super().__init__()
        self.simulations = simulations
        self.ship_sizes = [5, 4, 3, 3, 2]

    def get_move(self, board: Grid_D):
        """Get a move from ISMCTS algorithm. Takes a board, and returns
        a move
        """
        # Run simulation
        simulation_board = Grid_D.from_grid(board)
        new_board: Node = self.SO_ISMCTS(simulation_board, self.simulations)

        # Return chosen action
        return new_board.action

    def UCB1_select_best_child(self, node, C=0.7):
        # Applies UCB1 value to each child, and selects the child with the highest
        # value. Each child starts with value of infinity, so is always expanded first
        # if never expanded.
        best_value = float("-inf")
        best_nodes = []
        for child in node.children:
            if child.visits == 0:
                ucb1_value = float("inf")
            else:
                ucb1_value = (child.value / child.visits) + C * math.sqrt(
                    math.log(node.visits) / child.visits
                )
            if ucb1_value > best_value:
                best_value = ucb1_value
                best_nodes = [child]
            elif ucb1_value == best_value:
                best_nodes.append(child)

        if len(best_nodes) == 0:
            print("ERRRRRRR")
            return node
        return random.choice(best_nodes)

    def SELECT(self, v: Node, d: Grid_D):
        """
        Select implementation based on ISMCTS psuedocode, applied to python
        and implemented for battleship
        """
        while not self.is_terminal(v.state):
            # Traverse tree and select best child node until is fully expanded or leaf
            if v.is_fully_expanded():
                v = self.UCB1_select_best_child(v)
                d = deepcopy(v.state)
            else:
                break
        return v, d

    def EXPAND(self, parent_state: Node, curr_determ: Grid_D):
        """Expands a selected node, preparing it for rollout."""

        # Get legal untried moves
        legal_moves = set(self.get_legal_moves(curr_determ))
        current_actions = set([child.action for child in parent_state.children])
        untried_moves = legal_moves - current_actions
        to_remove = []

        # Remove moves which correspond to illegal moves
        for move in untried_moves:
            if parent_state.state.map[move[1]][move[0]] == Grid_D.SPACE["hit"]:
                to_remove.append(move)

        for move in to_remove:
            untried_moves.remove(move)

        if not untried_moves:
            print(f"No untried moves available for Node {parent_state.id}")
            return parent_state, curr_determ

        # Expand legal move. Add to tree and return
        move = random.choice(list(untried_moves))
        new_determ = self.apply_action(deepcopy(curr_determ), move)
        child_state = Node(new_determ, parent_state, move)
        parent_state.add_child(child_state)

        return child_state, new_determ

    def SIMULATE(self, d: Grid_D):
        """Simulate implementation as follows ISMCTS psuedocode, but in python
        and for battleship
        """
        # Create board to do random rollout
        simulation_state = deepcopy(d)
        legal_moves = self.get_legal_moves(simulation_state)
        total_hits = sum(
            cell == Grid_D.SPACE["hit"] for row in simulation_state.map for cell in row
        )

        # While board is not terminal
        while len(legal_moves) > 0 and total_hits < 17:
            move = random.choice(list(legal_moves))
            legal_moves.remove(move)
            x, y = move
            simulation_state = self.apply_action(simulation_state, move)
            if simulation_state.map[y][x] == Grid_D.SPACE["hit"]:
                total_hits += 1

        # Return reward of legal moves left (More moves left means better rollout)
        return len(legal_moves)

    def BACKPROPAGATE(self, r: float, v: Node):
        """Backpropagate and update visit counts and value for nodes"""
        count = 0
        while v is not None:
            count += 1
            v.value += r
            v.visits += 1
            v = v.parent

    def SO_ISMCTS(self, current_board, n: int = 1000):
        """Single Observer Information Set Monte Carlo Tree Search
        Follows ISMCTS psuedocode, but is similar to MCTS
        """
        root_node = Node(current_board, None, None)

        # For n iterations, run ISMCTS
        for _ in range(n):

            # Generate possible legal uniformly random configuration of board
            new_determinization = generate_valid_configuration(
                current_board, self.ship_sizes, 1000
            )
            new_state, new_determ = self.SELECT(root_node, new_determinization)

            if not self.is_terminal(new_state.state):
                new_state, new_determ = self.EXPAND(new_state, new_determ)

            reward = self.SIMULATE(new_determ)
            self.BACKPROPAGATE(reward, new_state)

        # Return best child (most visits)
        return max(root_node.children, key=lambda c: c.visits)

    def get_legal_moves(self, state: Grid_D):
        open_cells = state.getEmptySpaces()
        legal_moves = set(open_cells)
        return legal_moves

    def apply_action(self, state: Grid_D, action: Tuple[int, int]) -> Grid_D:
        """Guess at a ship location, and apply to grid"""
        x, y = action
        if state.map[y][x] == Grid_D.SPACE["potential_ship"]:
            state.map[y][x] = Grid_D.SPACE["hit"]
        else:
            state.map[y][x] = Grid_D.SPACE["miss"]
        return state

    def is_terminal(self, state: Node):
        """Checks if in terminal state (all ships sunk)"""
        total_ship_segments = sum(self.ship_sizes)
        if isinstance(state, (Grid, Grid_D)):
            hit_count = sum(
                cell == Grid_D.SPACE["hit"] for row in state.map for cell in row
            )
        else:
            hit_count = sum(
                cell == Grid_D.SPACE["hit"] for row in state.state.map for cell in row
            )
        return hit_count == total_ship_segments


def can_place_ship(grid, ship_size, x, y, direction):
    """Checks if ship placement on grid is valid"""
    if direction == Direction.HORIZONTAL:
        if x + ship_size > grid.cols:
            return False
        for i in range(ship_size):
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
    """Finds all valid ship placements given a board state"""
    valid_placements = []
    for y in range(grid.rows):
        for x in range(grid.cols):
            if can_place_ship(grid, ship_size, x, y, Direction.HORIZONTAL):
                valid_placements.append((x, y, Direction.HORIZONTAL))
            if can_place_ship(grid, ship_size, x, y, Direction.VERTICAL):
                valid_placements.append((x, y, Direction.VERTICAL))
    return valid_placements


def generate_all_configurations(grid, ship_sizes):
    """Generates all board configuration (Information set)"""
    all_placements = [
        find_valid_placements(grid, ship_size) for ship_size in ship_sizes
    ]

    # All permutations of ship placements (some valid some invalid)
    all_combinations = list(product(*all_placements))

    valid_configurations = []

    # Iterates through configurations, and finds up to a thresholded number of them
    # returns valid configurations
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


def matches_hits(grid: Grid_D, original_grid: Grid_D):
    """
    Checks to see if all hits on a board have a potential_ship placement
    otherwise, it would be an invalid placement
    """
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
    """Places a ship"""
    if direction == Direction.HORIZONTAL:
        for i in range(ship_size):
            grid.map[y][x + i] = place_ship_enum
    elif direction == Direction.VERTICAL:
        for i in range(ship_size):
            grid.map[y + i][x] = place_ship_enum


def generate_random_determinization(state: Grid_D, ship_sizes: list) -> Grid_D:
    """Generates a random determinization from the information set"""
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

            # Too many cells attempted, revert to generating the information set
            if count % 1000000 == 0:
                print(count)
                valid_configurations = generate_all_configurations(state, ship_sizes)
                matching_configurations = [
                    config
                    for config in valid_configurations
                    if matches_hits(config, state)
                ]
                return random.choice(matching_configurations)
    return grid


def generate_valid_configuration(
    state: Grid_D, ship_sizes: list, threshold: int
) -> Grid_D:
    """Generates a valid configuration for a set of ships on a given board"""
    all_placements = [
        find_valid_placements(state, ship_size) for ship_size in ship_sizes
    ]

    # Checks total number of ship combinations
    total_combinations = 1
    for placements in all_placements:
        total_combinations *= len(placements)

    # If below threshold, generate information set, otherwise generate random board
    if total_combinations <= threshold:
        valid_configurations = generate_all_configurations(state, ship_sizes)
        matching_configurations = [
            config for config in valid_configurations if matches_hits(config, state)
        ]
        return random.choice(matching_configurations)
    else:
        return generate_random_determinization(state, ship_sizes)
