import copy
import random
from typing import List, Optional, Tuple
from Grid_10 import Grid
from PlayerAI_10 import MoveStrategy
from Metrics_10 import Metrics
from CSP.CSP_rules import *
from CSP.CSP_helper import *

VARIABLES = ["S5", "S4", "S31", "S32", "S2"]

DOMAIN = set()
for x in range(10):
    for y in range(10):
        for v in [True, False]:
            DOMAIN.add((x,y,v))
FAILURE = 'Failure'

class Assignment:
    """
    Object so we can do proper deep copies
    """
    def __init__(self, assignment_map):
        self.map = assignment_map
    def copy(self):
        return copy.deepcopy(self)

class CSPAI(MoveStrategy):
    def __init__(self):
        self.prev_move = None # Setting this so we can track the board response
        self.hunting = False # for subproblem, coordinates of a hit
        self.assignment = default_assignment()
        self.sunk = [] # track ships we've both solved for and sunken
        self.best_guess = None # to track first move of backtracking
    # ---------------- Main Move Logic ----------------------
    def get_move(self, board: Grid) -> Tuple[int, int]:
        prev_result = self.get_prev_move_result(board)
        # 1. If solved, get non-sunk ship and begin early guess
        if is_solved(self.assignment.map):
            self.best_guess = self.get_guess_from_solved(board)
            return self.get_move_from_guess(board)

        # 2. If sunk, adjust hunting tracker and assignment
        elif prev_result == 'sunk':
            self.hunting = sunk_adjust_assignment(self.prev_move, self.hunting, board, self.assignment.map)
            # 2.a make sure our self.sunk is updated correctly
            sx, sy = self.prev_move
            size = board.map[sy][sx].size
            ship_id = 'S' + str(size)
            # tie breaker since 2 ships of size 3
            if board.map[sy][sx].size == 3:
                if 'S31' not in self.sunk:
                    ship_id = 'S31'
                else:
                    ship_id = 'S32'
            self.sunk.append(ship_id)
            self.prev_move = None

        # 3. Handle the previous move, may do Backtracking or Hunting subproblem
        self.handle_prev_move(board)

        # 4. return the move from the guess
        return self.get_move_from_guess(board)
    
    def get_move_from_guess(self, board: Grid) -> Tuple[int, int]:
        x,y,v = self.best_guess
        # 1. If we're hunting, get the point closest to initial point
        if self.hunting != False:
            direction = get_direction_to_coord((x,y), self.hunting[0][0])
            # 1.a we either need to go down or left over the shots we've already made
            if board.map[y][x] != Grid.SPACE['empty']:
                while board.map[y][x] != Grid.SPACE['empty']:
                    if v == True:
                        y += 1
                    else:
                        x -= 1
                self.prev_move = (x,y)
                return (x,y)
            # 2.a or go down or left to find the closest cell to first hunted cell
            else:
                closest_shot = move_towards(direction, (x,y), self.hunting[0][0], board)
                self.prev_move = closest_shot
                return closest_shot
        # 2. otherwise, just guess the first empty space in the guess
        ship = self.get_next_unsunk_ship()
        for x,y in get_full_ship_coords(self.best_guess, int(ship[1])):
            if board.map[y][x] == Grid.SPACE['empty']:
                self.prev_move = (x,y)
                return (x,y)
        # On the instance we don't find an empty space in our guess, something went wrong so we choose a random square
        print("MISTAKE?")
        choices = board.getEmptySpaces()
        choice = random.choice(choices)
        # save prev move, just assuming after this function we call make_move
        self.prev_move = choice
        return (0, 0) if len(choices) == 0 else choice
    def get_guess_from_solved(self, board: Grid) -> Tuple[int,int,bool]:
        prev_result = self.get_prev_move_result(board)
        # 1. If prev result is sunk, add that ship to the sunk list
        if prev_result == 'sunk':
            ship = self.get_next_unsunk_ship()
            self.sunk.append(ship)
        # 2. Get next un-sunk variable and return that as best guess
        ship = self.get_next_unsunk_ship()
        self.best_guess = self.assignment.map[ship].pop()
        self.assignment.map[ship] = [self.best_guess]
        return self.best_guess
    def get_next_unsunk_ship(self) -> Optional[str]:
        for ship in VARIABLES:
            if ship not in self.sunk:
                return ship
        return None
    def handle_prev_move(self, board: Grid) -> None:
        prev_result = self.get_prev_move_result(board)
        # 1. If hunting, do that subproblem instead
        if self.hunting != False:
            self.hunt(board)
        
        # 2. If hit, enter subproblem
        elif prev_result == 'hit':
            self.hunting = [[]]
            self.hunt(board)
        
        # 3. If miss, adjust assignment
        elif prev_result == 'miss':
            miss_adjust_assignment(self.prev_move, self.assignment.map)
            result = self.backtrack(self.assignment)
        # 4. If haven't made a move yet, just do normal backtrack
        else:
            result = self.backtrack(self.assignment)

    # ------------ Algorithms -----------------

    def backtrack(self, assignment: Assignment):
        """
        Sets self.best_guess
        CSP root algorithm, once a hypothetical solution is found it sets self.best_guess to the first assumed value
        """
        if is_solved(assignment.map):
            return assignment
        MRV_ship = self.get_MRV_ship(assignment.map)
        if len(assignment.map[MRV_ship]) == 0:
            return FAILURE
        ordered_domains = self.ordered_domain_values(MRV_ship, assignment)
        for X, Y, V in ordered_domains:
            # for this adjusted problem, we don't actually need to do full backtracking, so instead we're returning early
            self.best_guess = (X,Y,V)
            return assignment
            new_assignment = assignment.copy()
            adjust_assignment(MRV_ship, (X,Y,V), new_assignment.map)
            result = self.backtrack(new_assignment)
            if result != FAILURE:
                # Since we're ordering the domain by how restrictive it is, our best shot is the first assumption we make
                self.best_guess = (X,Y,V)
                return result
        
        return FAILURE

    def ordered_domain_values(self, ship: str, assignment: Assignment) -> List[Tuple[int, int, bool]]:
        """
        returns sorted list of domain values for some ship
        highest priority goes to the one that makes the biggest difference if hit/miss
        This is probably the most expensive function
        """
        sum_domain = sum_domains(assignment.map)
        domain_values = []
        for X, Y, V in assignment.map[ship]:
            shot = (X, Y) # just doing this for clarity
            pretend_hit_assignment = assignment.copy()
            pretend_miss_assignment = assignment.copy()
            adjust_assignment(ship, (X,Y,V), pretend_hit_assignment.map)
            miss_adjust_assignment(shot, pretend_miss_assignment.map)
            hit_reduction = sum_domain - sum_domains(pretend_hit_assignment.map)
            miss_reduction = sum_domain - sum_domains(pretend_miss_assignment.map)
            total_reduction = hit_reduction + miss_reduction
            domain_values.append((total_reduction, (X,Y,V)))
        ordered_values_pairs = sorted(domain_values, key=lambda item: item[0], reverse=True)
        ordered_values = [value for _, value in ordered_values_pairs]
        return ordered_values

    def get_MRV_ship(self, assignment_map: dict) -> str:
        """
        will not return length 1 assignments
        will return length 0 assignment for failed assignment
        will return other lengths as possible assignments
        """
        mrv_ship = 'X'
        mrv_ship_domain = 201
        for ship in VARIABLES:
            ship_domain = len(assignment_map[ship])
            if ship_domain < mrv_ship_domain and ship_domain != 1:
                mrv_ship = ship
                mrv_ship_domain = ship_domain
        return mrv_ship
    
    # ------------------- Hunting Subproblem ---------------------
    def hunt(self, board: Grid) -> None:
        """
        sets self.best_guess
        hunts the first set of coords in self.hunting
        """
        # 1. Adjust based on last move result
        if self.get_prev_move_result(board) == 'miss':
            miss_adjust_assignment(self.prev_move, self.assignment.map)
        elif self.get_prev_move_result(board) == 'hit':
            self.hunting[0].append(self.prev_move)

        # 2. try to find potential valid ship to use
        prey_ship = self.get_prey_ship(self.assignment, board)
        # 3. if no valid ship, handle edge cases and try again
        if prey_ship == None:
            # 3.a We have too many shots
            biggest_ship = self.get_next_unsunk_ship()
            biggest_ship_size = int(biggest_ship[1])
            if len(self.hunting[0]) > biggest_ship_size:
                x1,y1 = self.hunting[0][0]
                x2,y2 = self.hunting[0][1]
                vertical = x1 == x2
                # if vertical, guess lowest y value and "highest"
                if vertical:
                    lowest_y = min([y for x,y in self.hunting[0]])
                    highest_y = max([y for x,y in self.hunting[0]])
                    highest_y = highest_y - biggest_ship_size + 1
                    lowest_assignment = self.assignment.copy()
                    lowest_assignment.map[biggest_ship] = [(x1, lowest_y, vertical)]
                    highest_assignment = self.assignment.copy()
                    highest_assignment.map[biggest_ship] = [(x1, highest_y, vertical)]
                    # One of these should adjust best_guess
                    self.handle_hunting_edge(board, biggest_ship, lowest_assignment)
                    self.handle_hunting_edge(board, biggest_ship, highest_assignment)
                # if horizontal, guess highest x value and "lowest"
                else:
                    highest_x = max([x for x,y in self.hunting[0]])
                    lowest_x = min([x for x,y in self.hunting[0]])
                    lowest_x = lowest_x + biggest_ship_size - 1
                    lowest_assignment = self.assignment.copy()
                    lowest_assignment.map[biggest_ship] = [(lowest_x, y1, vertical)]
                    highest_assignment = self.assignment.copy()
                    highest_assignment.map[biggest_ship] = [(highest_x, y1, vertical)]
                    # One of these should adjust best_guess
                    self.handle_hunting_edge(board, biggest_ship, lowest_assignment)
                    self.handle_hunting_edge(board, biggest_ship, highest_assignment)
            # 3.b We have no room for shots
            else:
                self.handle_no_valid_ship()
                # we already handled prev_move so we don't want to process again
                self.prev_move = None
                self.hunt(board)

    def get_prey_ship(self, assignment: Assignment, board: Grid) -> Optional[str]:
        # 1. Iterate through non-sunk ships (biggest first)
        for ship in VARIABLES:
            if ship in self.sunk:
                continue
            # 2. Make adjustments
            new_assignment = assignment.copy()
            # 2.a if there are multiple hunting lists, make sure to disinclude the others
            if len(self.hunting) > 1:
                for i in range(1,len(self.hunting)):
                    miss_adjust_assignment(self.hunting[i][0], new_assignment.map)
            hit_adjust_assignment(ship, self.hunting[0], new_assignment.map)
            # 3. If we have a successful assignment, return early
            result = self.backtrack(new_assignment)
            if result != FAILURE:
                # if our ship is fully assigned, make sure there's an empty space
                if len(new_assignment.map[ship]) == 1:
                    if ship_has_empty_spaces(board, ship, new_assignment):
                        self.best_guess = new_assignment.map[ship].pop()
                        return ship
                    else: # potentially 2 edge cases
                        return self.handle_hunting_edge(board, ship, new_assignment)
                else:
                    return ship
        # 4. No valid ship, return None
        return None
    
    def handle_hunting_edge(self, board: Grid, ship: str, assignment: Assignment) -> Optional[str]:
        """
        There's an assignment for the ship but every space has been used.
        Return's none if there are no free spaces on either side, otherwise sets best guess to the next free space and returns the ship
        """
        x,y,v = assignment.map[ship][0] # TODO: might have to change this to a pop
        size = int(ship[1])
        # 1. If there's a free space on one of the edges, place that as best guess and return the ship
        # 2. If there are no free edges, return None, each spot is its own hunting problem
        if v == True:
            above_empty = y > 0 and board.map[y-1][x] == Grid.SPACE['empty']
            below_empty = y+size <= 9 and board.map[y+size][x] == Grid.SPACE['empty']
            if not above_empty and not below_empty:
                return None # 2.
            elif above_empty:
                self.best_guess = (x,y-1,v)
            elif below_empty:
                self.best_guess = (x,y+size,v)
        elif v == False:
            left_empty = x < 9 and board.map[y][x+1] == Grid.SPACE['empty']
            right_empty = x-size >= 0 and board.map[y][x-size] == Grid.SPACE['empty']
            if not left_empty and not right_empty:
                return None # 2.
            elif left_empty:
                self.best_guess = (x+1,y,v)
            elif right_empty:
                self.best_guess = (x-size,y,v)
        return ship
    def handle_no_valid_ship(self) -> None:
        new_hunting = []
        for coord in self.hunting[0]:
            new_hunting.append([coord])
        self.hunting = new_hunting
# ------------------- Setup ---------------------------

def default_assignment() -> Assignment:
    """
    All placements for ships that are in bounds
    """
    assignment_map = {}
    for var in VARIABLES:
        assignment_map[var] = set(DOMAIN)
        out_of_bounds_adjust(var, assignment_map)
    return Assignment(assignment_map)