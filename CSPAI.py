from typing import Tuple
from PlayerAI_10 import MoveStrategy


# From my HW2 solution
class Assignment:
    """
    Object so we can do proper deep copies
    """
    ship_labels = ["5", "4", "31", "32", "2"]
    def __init__(self):
        self.variables = [ # n = 15
            f'V{label}' for label in self.ship_labels ] + [ # Vertical
            f'X{label}' for label in self.ship_labels ] + [ # X coord
            f'Y{label}' for label in self.ship_labels ] # Y Coord
        self.domain = [x for x in range(10)] + [True, False] # d = 12
        
        self.assignment_map = {}
        for var in self.variables:
            self.assignment_map[var] = set(self.domain)
    
    def assignment(self):
        return self.assignment_map
    
class ASPAI(MoveStrategy):
    def __init__(self):
        # define an assignment
        self
        pass
    def get_move(self, move: str) -> Tuple[int, int]:

        return super().get_move(move)