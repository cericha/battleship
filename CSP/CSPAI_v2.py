
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


class CSPAI(MoveStrategy):
    def __init__(self):
        self.prev_move = None
        self.hunting = False # for subproblem
        self.hunting_direction = None # for helping subproblem
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
            self.hunting = False
            self.sunk_adjust_assignment(self.prev_move, self.assignment)
        elif prev_result == 'miss':
            self.miss_adjust_assignment(self.prev_move, self.assignment)
        
        # Run augmented CSP 'backtracking'
        return self.backtrack(board, self.assignment.map)
    # ------------ Algorithms -----------------
    def backtrack(self, board, assignment):
        MRV_ship = self.get_MRV_ship(board)
        best_shot = (-1,-1)
        best_reduction = 0
        for X, Y, V in assignment.map[MRV_ship]:
            shot = (X, Y) # just doing this for clarity
            pretend_assignment = assignment.copy()
            self.adjust_assignment(MRV_ship, (X,Y,V), pretend_assignment.map)
            reduction = self.sum_domains(assignment) - self.sum_domains(pretend_assignment)
            if reduction > best_reduction:
                best_shot = shot
                best_reduction = reduction
        self.prev_move = best_shot
        return best_shot
    def hunt(self, board):
        # TODO: implement
        # 1. Decide direction
        pass
    # ------------ Helper ---------------------
    def get_MRV_ship(self, board):
        # TODO: implement
        pass
    def sum_domains(self, assignment):
        # TODO: implement
        pass

    def adjust_assignment(self, var, value, assignment_map):
        # TODO: implement
        pass
    def sunk_adjust_assignment(self, board, assignment_map):
        # TODO: implement
        x, y = self.prev_move
        ship_id = 'S' + board.map[y][x].size
        if board.map[y][x].size == 3:
            ship_id = self.size_3_ship_id()
        ship_head = self.get_ship_head()
        self.hunting_direction = None
    def miss_adjust_assignment(self, board, assignment_map):
        # TODO: implement
        pass

    def get_ship_id(self, hit_coord, board):
        # TODO: implement
        pass
    def size_3_ship_id(self):
        # TODO: implement
        pass


    class Assignment:
        """
        Object so we can do proper deep copies
        """
        def __init__(self, assignment_map):
            self.map = assignment_map
        def copy(self):
            return copy.deepcopy(self)
    
    def default_assignment(self):
        assignment_map = {}
        for var in VARIABLES:
            assignment_map[var] = set(DOMAIN)
            self.out_of_bounds_adjust(var, assignment_map)
        return self.Assignment(assignment_map)
    
    def out_of_bounds_adjust(self, var, assignment_map):
        # TODO: implement
        pass
