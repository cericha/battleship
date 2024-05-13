import copy
from typing import Tuple
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
        self.sunk = []
        self.best_guess = None # to track first move of backtracking
        self.metrics = Metrics(0,0)
    
    def move_from_guess(self, board):
        """
        returns coordinate of appropriate shot based on our best guess
        """
        x,y,v = self.best_guess
        # 1. this is for when we're guessing a ship but already got the head parts
        while board.map[y][x] != Grid.SPACE['empty']:
            if v == True:
                y += 1
            else:
                x -= 1
        # 2. if we're hunting we want to be as close as possible to where we started hunting
        if self.hunting != False and (x,y) != self.hunting[0][0]:
            direction = get_direction_to_coord((x,y), self.hunting[0][0])
            closest_shot = move_towards(direction, (x,y), self.hunting[0][0], board)
            self.best_guess = (closest_shot[0], closest_shot[1], v)
            self.prev_move = closest_shot
            return closest_shot
        # 3. make sure to set prev_move so we can get the result of our shot next move
        self.prev_move = (x,y)
        # 4. return the shot we should make
        return (x,y)
    
    def get_move(self, board: Grid) -> Tuple[int, int]:
        # 1. get information about previous shot
        prev_result = self.get_prev_move_result(board)
        # 2. In sub-problem of hunting
        if self.hunting != False and prev_result != 'sunk':
            self.hunt(board, self.assignment)
            return self.move_from_guess(board)

        # 3. Adjust Alogirthm based on prev_result
        # 3.a On hit, we begin hunting
        elif prev_result == 'hit':
            self.hunting = [[]]
            self.hunt(board, self.assignment)
            return self.move_from_guess(board)
        # 3.b On sunk, we adjust our assignment, then either keep hunting or move on
        elif prev_result == 'sunk':
            self.hunting = sunk_adjust_assignment(self.prev_move, self.hunting, board, self.assignment.map)
            x,y = self.prev_move
            size = board.map[y][x].size
            if size == 3:
                self.sunk.append(size_3_ship_id(self.assignment.map))
            else:
                self.sunk.append('S'+str(size))
            # if there are still spaces that have been hit, continue hunting
            if self.hunting != False:
                self.hunt(board, self.assignment)
                return self.move_from_guess(board)
            # otherwise keep going
        # 3.c On miss, we simply adjust our assignment
        elif prev_result == 'miss':
            miss_adjust_assignment(self.prev_move, self.assignment.map)
        
        # 4. If we already know for sure where everything is, just start going for it
        if is_solved(self.assignment.map):
            for variable in VARIABLES:
                if variable not in self.sunk:
                    self.best_guess = self.assignment.map[variable].pop()
                    self.assignment.map[variable] = self.best_guess
                    return self.move_from_guess(board)
        # 5. Run augmented CSP 'backtracking'. the backtracking sets up our "best guess"
        self.backtrack(board, self.assignment)
        # 6. Return the move from our best guess
        return self.move_from_guess(board)
    
    # ------------ Algorithms -----------------

    def backtrack(self, board, assignment: Assignment):
        """
        CSP root algorithm, once a hypothetical solution is found it sets self.best_guess to the first assumed value
        """
        if is_solved(assignment.map):
            return assignment
        MRV_ship = self.get_MRV_ship(assignment.map)
        if len(assignment.map[MRV_ship]) == 0:
            return FAILURE
        ordered_domains = self.ordered_domain_values(MRV_ship, assignment)
        for X, Y, V in ordered_domains:
            new_assignment = assignment.copy()
            adjust_assignment(MRV_ship, (X,Y,V), new_assignment.map)
            result = self.backtrack(board, new_assignment)
            if result != FAILURE:
                # Since we're ordering the domain by how restrictive it is, our best shot is the first assumption we make
                self.best_guess = (X,Y,V)
                return result
        
        return FAILURE
    def ordered_domain_values(self, ship, assignment: Assignment):
        """
        returns sorted list of domain values for some ship
        highest priority goes to the one that makes the biggest difference if hit/miss
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
        ordered_values_pairs = sorted(domain_values, key=lambda item: item[0])
        ordered_values_pairs.reverse()
        ordered_values = [value for _, value in ordered_values_pairs]
        return ordered_values

    def get_MRV_ship(self, assignment_map):
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
    
    # ------------------- Hunting Sub-Problem --------------------
    def hunt(self, board, assignment):
        """
        If we know we've hit a boat, first adjust the mrv_ship and then try best guess
        """
        # 1. Adjust based on last move result
        if self.get_prev_move_result(board) == 'miss':
            miss_adjust_assignment(self.prev_move, self.assignment.map)
        elif self.get_prev_move_result(board) == 'hit':
            self.hunting[0].append(self.prev_move)
        
        # 2. try to find potential valid ship to use
        MRV_ship = self.get_MRV_ship(assignment.map)
        new_assignment = assignment.copy()
        # 2.a if there are multiple hunting lists, make sure to disinclude the others
        if len(self.hunting) > 1:
            for i in range(1,len(self.hunting)):
                miss_adjust_assignment(self.hunting[i][0], new_assignment.map)
        hit_adjust_assignment(MRV_ship, self.hunting[0], new_assignment.map)
        result = self.backtrack(board, new_assignment)
        # 2.b if the chosen ship doesn't work, keep downgrading size until we find working or edge case
        while result == FAILURE:
            MRV_ship_size = int(MRV_ship[1])
            new_size = MRV_ship_size - 1
            if new_size==3:
                MRV_ship = size_3_ship_id(self.assignment.map)
            elif new_size != 1:
                MRV_ship = 'S' + str(new_size)
            else: # edge case, no ship works
                break
            new_assignment = self.assignment.copy()
            hit_adjust_assignment(MRV_ship, self.hunting[0], new_assignment.map)
            result = self.backtrack(board, new_assignment)
        
        # 3. check for single option edge case
        if len(new_assignment.map[MRV_ship]) == 1:
            self.best_guess = new_assignment.map[MRV_ship].pop()
            guess_coords = get_full_ship_coords(self.best_guess, int(MRV_ship[1]))
            for x,y in guess_coords:
                # 3.a it's valid because there's an empty space we can fire on
                if board.map[y][x] == Grid.SPACE['empty']:
                    return
            # 4. it's not valid because there are no empty spaces
            # two options:
            # 4.a both ends cut off, each coord is its own hunting problem
            # 4.b some end must be free, return that for now
            x,y,v = self.best_guess
            
            size = int(MRV_ship[1])
            if v == True:
                above_empty = board.map[y-1][x] == Grid.SPACE['empty'] and y > 0
                below_empty = board.map[y+size][x] == Grid.SPACE['empty'] and y+size <= 9
                # 4.a 
                if not above_empty and not below_empty:
                    new_hunting = []
                    for coord in self.hunting[0]:
                        new_hunting.append([coord])
                    self.hunting = new_hunting
                    return self.hunt(board, assignment)
                # 4.b
                elif above_empty:
                    self.best_guess = (x,y-1,v)
                elif below_empty:
                    self.best_guess = (x,y+size,v)
            elif v == False:
                left_empty = board.map[y][x+1] == Grid.SPACE['empty'] and x < 9
                right_empty = board.map[y][x-size] == Grid.SPACE['empty'] and x-size >= 0
                # 4.a
                if not left_empty and not right_empty:
                    
                    new_hunting = []
                    for coord in self.hunting[0]:
                        new_hunting.append([coord])
                    self.hunting = new_hunting
                    return self.hunt(board, assignment)
                # 4.b
                elif left_empty:
                    self.best_guess = (x+1,y,v)
                elif right_empty:
                    self.best_guess = (x-size,y,v)

        

def default_assignment():
    """
    All placements for ships that are in bounds
    """
    assignment_map = {}
    for var in VARIABLES:
        assignment_map[var] = set(DOMAIN)
        out_of_bounds_adjust(var, assignment_map)
    return Assignment(assignment_map)