
import copy
from typing import Tuple
from Grid_10 import Grid
from PlayerAI_10 import MoveStrategy


VARIABLES = ["S5", "S4", "S31", "S32", "S2"]

DOMAIN = set()
for x in range(10):
    for y in range(10):
        for v in [True, False]:
            DOMAIN.add((x,y,v))

OPPOSITE_DIRECTIONS = {
    'N' : 'S',
    'E' : 'W',
    'S' : 'N',
    'W' : 'E'
}


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
        self.prev_move = None
        self.hunting = False # for subproblem
        self.hunting_direction = None
        self.assignment = self.default_assignment()
        
    def get_move(self, board: Grid) -> Tuple[int, int]:
        prev_result = self.get_prev_move_result(board)
        # In sub-problem of hunting
        if self.hunting and prev_result != 'sunk':
            return self.hunt(board)

        # Adjust Alogirthm based on prev_move (if appropriate)
        elif prev_result == 'hit':
            self.hunting = True
            return self.hunt(board)
        elif prev_result == 'sunk':
            self.sunk_adjust_assignment(self.prev_move, self.assignment)
            # try get move again incase our sunk ship doesn't account for all hit spaces 
            return self.get_move(board)
        elif prev_result == 'miss':
            self.miss_adjust_assignment(self.prev_move, self.assignment)
        
        # Run augmented CSP 'backtracking'
        return self.backtrack(board, self.assignment.map)
    
    # ------------ Algorithms -----------------

    def backtrack(self, board, assignment: Assignment):
        MRV_ship = self.get_MRV_ship(assignment.map)
        best_shot = (-1,-1)
        best_reduction = 0
        sum_domain = self.sum_domains(assignment)
        # this isn't the normal for each loop for CSP, it is what would normally happen when ordering our domain values
        # I'm putting it here because it's what will return us the move
        for X, Y, V in assignment.map[MRV_ship]:
            shot = (X, Y) # just doing this for clarity
            pretend_hit_assignment = assignment.copy()
            pretend_miss_assignment = assignment.copy()
            self.adjust_assignment(MRV_ship, (X,Y,V), pretend_hit_assignment.map)
            self.miss_adjust_assignment(shot, pretend_miss_assignment)
            hit_reduction = sum_domain - self.sum_domains(pretend_hit_assignment)
            miss_reduction = sum_domain - self.sum_domains(pretend_miss_assignment)
            total_reduction = hit_reduction + miss_reduction
            if total_reduction > best_reduction:
                best_shot = shot
                best_reduction = total_reduction
        self.prev_move = best_shot
        return best_shot
    def hunt(self, board, assignment):
        """
        If we know we've hit a boat, try to sink it so we can get a full assignment for a ship
        """
        # TODO: implement. watchout for edge cases where we follow a direction but DONT sink
        move = (-1,-1)
        prev_result = self.get_prev_move_result(board)
        if self.hunting_direction == None:
            # Decide which direction to go
            # for now do random. TODO: maybe do it based on domain reduction?
            pass
        elif prev_result == 'hit':
            pass
        elif prev_result == 'miss':
            pass
        self.prev_move = move
        return move
    # ------------ Helper ---------------------
    def get_MRV_ship(self, assignment_map):
        mrv_ship = 'X'
        mrv_ship_domain = 201
        for ship in VARIABLES:
            ship_domain = len(assignment_map[ship])
            if ship_domain < mrv_ship_domain and ship_domain != 1:
                mrv_ship = ship
                mrv_ship_domain = ship_domain
        return mrv_ship
    def sum_domains(self, assignment_map):
        sum_total = 0
        for ship in VARIABLES:
            sum_total += len(assignment_map[ship])
        return sum_total

    def adjust_assignment(self, ship, value, assignment_map):
        # TODO: decide on whether or not to recursively call
        assignment_map[ship] = value
        size = ship[1]
        hit_ship_coords = self.get_full_ship_coords(value, size)
        for other_ship in VARIABLES:
            if other_ship != ship:
                to_be_removed = []
                for other_value in assignment_map[other_ship]:
                    other_coords = self.get_full_ship_coords(other_value, other_ship[1])
                    for cell in other_coords:
                        # if this assignment overlaps at all with the sunk ship, then remove it
                        if cell in hit_ship_coords:
                            to_be_removed.append(other_value)
                for item in to_be_removed:
                    assignment_map[other_ship].remove(item)
                    # TODO: Should we check for if we've found a new assignment? that would be great for us cus we could sink
        
        
    def sunk_adjust_assignment(self, board, assignment_map):
        """
        If we've sunk a ship, travel in the opposite direction that was used for hunting until we've marked all hits.
        Edge case if we accidentally sink a ship that was not originally hit
        """
        # TODO: implement
        x, y = self.prev_move
        ship_id = 'S' + board.map[y][x].size
        if board.map[y][x].size == 3:
            ship_id = self.size_3_ship_id()
        ship_head = self.get_ship_head()
        self.hunting_direction = None

        # If we keep traveling the direction and see a hit, that means we need to continue hunting

    def miss_adjust_assignment(self, coord, assignment_map):
        """
        If we miss on some coord, any assignment that places the ship on that coord is invalid
        """
        x_miss, y_miss = coord
        for ship in VARIABLES:
            size = ship[1]
            to_be_removed = []
            for X,Y,V in assignment_map[ship]:
                if V == True and X == x_miss and Y <= y_miss-size:
                    to_be_removed.append((X,Y,V))
                elif V == False and Y == y_miss and X > x_miss+size:
                    to_be_removed.append((X,Y,V))
            for item in to_be_removed:
                assignment_map[ship].remove(item)

    def size_3_ship_id(self, assignment_map):
        """
        since there are 2 ships with size 3, we want to distinguish them when needing a label
        """
        if len(assignment_map['S31']) == 1:
            return 'S32'
        return 'S31'
    def get_full_ship_coords(self, value, size):
        hit_coords = []
        x, y, v = value
        if v == True:
            for i in range(size):
                hit_coords.append((x, y+i))
        else:
            for i in range(size):
                hit_coords.append((x-i, y))
        return hit_coords

    def default_assignment(self):
        """
        All placements for ships that are in bounds
        """
        assignment_map = {}
        for var in VARIABLES:
            assignment_map[var] = set(DOMAIN)
            self.out_of_bounds_adjust(var, assignment_map)
        return self.Assignment(assignment_map)
    
    def out_of_bounds_adjust(self, var, assignment_map):
        size = int(var[1])
        to_be_removed = []
        for X,Y,V in assignment_map[var]:
            if V == True and Y > 10-size: # magic 10, sorry. just grid size
                to_be_removed.append((X,Y,V)) # goes down too much
            elif V == False and X < size-1:
                to_be_removed.append((X,Y,V)) # goes left too much
        for item in to_be_removed:
            assignment_map[var].remove(item)
