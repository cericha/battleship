import copy
from typing import Tuple
from PlayerAI_10 import MoveStrategy
from battleship.Grid_10 import Grid
from Rules import *

SHIP_LABELS = ["5", "4", "31", "32", "2"]

VARIABLES = [ # n = 15
f'V{label}' for label in SHIP_LABELS ] + [ # Vertical
f'X{label}' for label in SHIP_LABELS ] + [ # X coord
f'Y{label}' for label in SHIP_LABELS ] # Y Coord

# VARIABLES = set(SHIP_LABELS) # n = 5

DOMAIN = set([x for x in range(10)] + [True, False]) # d = 12

# d = 200, every x,y combo and then verticality
# DOMAIN = set()
# for x in range(10):
#     for y in range(10):
#         for v in [True, False]:
#             DOMAIN.add((x,y,v))

RULES = {
    'vertical_domain' : vertical_domain,
    'coord_domain' : coord_domain,
    # 'no_out_of_bounds_v' : None,
    'no_out_of_bounds' : None,
    'no_overlap' : None,

}

# From my HW2 solution
class Assignment:
    """
    Object so we can do proper deep copies
    """
    def __init__(self, assignment_map = None):
        # Start off with every variable having the possibility of every domain value
        if assignment_map==None:
            
            self.assignment_map = {}
            for var in VARIABLES:
                self.assignment_map[var] = set(DOMAIN) # copy of domain
        # create with assignment map
        else:
            self.assignment_map = assignment_map

    def assignment(self):
        return self.assignment_map
    
    def give_assignment(self, var, val):
        """
        After assigning some variable with some value
        """
        # if var not in self.variables:
        #     return False
        if val in self.assignment_map[var]:
            self.assignment_map[var] = set([val])
            return True
        return False
    
    def apply_rule(self, rule_function, params):
        rule_function(self.assignment_map, params)

    def copy(self):
        return copy.deepcopy(self)
    
class CSPAI(MoveStrategy):
    def __init__(self):
        # define an assignment
        self.assignment = Assignment()
        self.la
        pass
    def get_next_biggest_ship(self):
        """
        returns label for biggest ship that is not fully assigned
        """
        for ship_label in SHIP_LABELS:
            X_assigned = len(self.assignment()['X'+ship_label]) == 1
            Y_assigned = len(self.assignment()['Y'+ship_label]) == 1
            V_assigned = len(self.assignment()['V'+ship_label]) == 1
            if not X_assigned or not Y_assigned or not V_assigned:
                return ship_label
        return "All ships assigned"
    def sink_ship(self):
        pass
    def get_move(self, board: Grid) -> Tuple[int, int]:
        # See if last move was a hit

        # get MRV
        # choose domain value based on how much it restricts future choices
        if last_move_hit():
            return self.sink_ship()
        else:
            return self.find_ship()
        return (0,0)